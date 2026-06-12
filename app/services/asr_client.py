import json
import time
import struct
import gzip
import uuid
import logging
import wave
import io
import subprocess
import os
from typing import Optional, Dict, Any, List, Tuple

# 尝试导入pydub用于音频格式转换
try:
    from pydub import AudioSegment
    has_pydub = True
except ImportError:
    has_pydub = False
    logging.warning("pydub not installed, audio format conversion may not work")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 常量定义
DEFAULT_SAMPLE_RATE = 16000

class ProtocolVersion:
    V1 = 0b0001

class MessageType:
    CLIENT_FULL_REQUEST = 0b0001
    CLIENT_AUDIO_ONLY_REQUEST = 0b0010
    SERVER_FULL_RESPONSE = 0b1001
    SERVER_ERROR_RESPONSE = 0b1111

class MessageTypeSpecificFlags:
    NO_SEQUENCE = 0b0000
    POS_SEQUENCE = 0b0001
    NEG_SEQUENCE = 0b0010
    NEG_WITH_SEQUENCE = 0b0011

class SerializationType:
    NO_SERIALIZATION = 0b0000
    JSON = 0b0001

class CompressionType:
    GZIP = 0b0001


class ASRConfig:
    def __init__(self, app_id: str, access_token: str, secret_key: str, base_url: str = "http://10.125.110.103:8004/v1"):
        self.app_id = app_id
        self.access_token = access_token
        self.secret_key = secret_key
        self.base_url = base_url


class ASRError(Exception):
    pass


class CommonUtils:
    @staticmethod
    def gzip_compress(data: bytes) -> bytes:
        return gzip.compress(data)

    @staticmethod
    def gzip_decompress(data: bytes) -> bytes:
        return gzip.decompress(data)

    @staticmethod
    def judge_wav(data: bytes) -> bool:
        if len(data) < 44:
            return False
        result = data[:4] == b'RIFF' and data[8:12] == b'WAVE'
        logger.info(f"judge_wav: len={len(data)}, RIFF={data[:4]}, WAVE={data[8:12]}, result={result}")
        return result

    @staticmethod
    def read_wav_info(data: bytes) -> Tuple[int, int, int, int, bytes]:
        if len(data) < 44:
            raise ValueError("Invalid WAV file: too short")
            
        # 解析WAV头
        chunk_id = data[:4]
        if chunk_id != b'RIFF':
            raise ValueError("Invalid WAV file: not RIFF format")
            
        format_ = data[8:12]
        if format_ != b'WAVE':
            raise ValueError("Invalid WAV file: not WAVE format")
            
        # 解析fmt子块
        audio_format = struct.unpack('<H', data[20:22])[0]
        num_channels = struct.unpack('<H', data[22:24])[0]
        sample_rate = struct.unpack('<I', data[24:28])[0]
        bits_per_sample = struct.unpack('<H', data[34:36])[0]
        
        logger.info(f"WAV file info: audio_format={audio_format}, num_channels={num_channels}, sample_rate={sample_rate}, bits_per_sample={bits_per_sample}")
        
        # 查找data子块
        pos = 36
        while pos < len(data) - 8:
            subchunk_id = data[pos:pos+4]
            subchunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
            logger.info(f"Found subchunk: {subchunk_id}, size: {subchunk_size}, pos: {pos}")
            if subchunk_id == b'data':
                wave_data = data[pos+8:pos+8+subchunk_size]
                logger.info(f"Found data subchunk, size: {len(wave_data)} bytes")
                return (
                    num_channels,
                    bits_per_sample // 8,
                    sample_rate,
                    subchunk_size // (num_channels * (bits_per_sample // 8)),
                    wave_data
                )
            pos += 8 + subchunk_size
            
        raise ValueError("Invalid WAV file: no data subchunk found")

    @staticmethod
    def convert_to_wav(audio_data: bytes) -> bytes:
        """将音频数据转换为WAV格式"""
        logger.info(f"convert_to_wav: audio_data size={len(audio_data)} bytes")
        
        if CommonUtils.judge_wav(audio_data):
            logger.info("Audio is already WAV format")
            return audio_data
        
        # 如果音频数据太小，直接返回原始数据
        if len(audio_data) < 100:
            logger.warning(f"Audio data too small: {len(audio_data)} bytes, returning as is")
            return audio_data
        
        # 尝试使用pydub转换音频格式
        if has_pydub:
            try:
                # 使用pydub转换音频格式
                audio = AudioSegment.from_file(io.BytesIO(audio_data))
                
                # 转换为16kHz, 16-bit, mono
                audio = audio.set_frame_rate(16000)
                audio = audio.set_sample_width(2)  # 16-bit
                audio = audio.set_channels(1)  # mono
                
                # 导出为WAV格式
                output = io.BytesIO()
                audio.export(output, format="wav")
                wav_data = output.getvalue()
                
                logger.info(f"Converted audio to WAV format using pydub, size: {len(wav_data)} bytes")
                return wav_data
            except Exception as e:
                logger.error(f"Error converting audio format with pydub: {e}")
                # 如果pydub转换失败，尝试使用ffmpeg
                pass
        
        # 尝试使用ffmpeg转换音频格式
        try:
            # 创建临时文件
            temp_input = "temp_input.audio"
            
            # 写入临时文件
            with open(temp_input, 'wb') as f:
                f.write(audio_data)
            
            # 使用ffmpeg转换音频格式，输出到标准输出
            cmd = [
                "ffmpeg", "-v", "quiet", "-y", "-i", temp_input,
                "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000",
                "-f", "wav", "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                # 如果ffmpeg转换失败，尝试手动创建WAV文件头
                return CommonUtils._create_wav_header(audio_data)
            
            wav_data = result.stdout
            
            # 删除临时文件
            try:
                os.remove(temp_input)
            except OSError as e:
                logger.warning(f"Failed to remove temp files: {e}")
            
            logger.info(f"Converted audio to WAV format using ffmpeg, size: {len(wav_data)} bytes")
            return wav_data
        except FileNotFoundError:
            logger.warning("FFmpeg not found, trying manual WAV header creation")
            return CommonUtils._create_wav_header(audio_data)
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return CommonUtils._create_wav_header(audio_data)

    @staticmethod
    def _create_wav_header(audio_data: bytes) -> bytes:
        """手动创建WAV文件头"""
        try:
            # 创建WAV文件头
            sample_rate = 16000
            channels = 1
            sample_width = 2  # 16-bit
            
            # 计算音频数据大小
            data_size = len(audio_data)
            
            # 如果音频数据太小，返回原始数据
            if data_size < 100:
                logger.warning(f"Audio data too small: {data_size} bytes, returning as is")
                return audio_data
            
            # 创建WAV文件头
            wav_header = bytearray()
            
            # RIFF头
            wav_header.extend(b'RIFF')
            wav_header.extend(struct.pack('<I', 36 + data_size))
            wav_header.extend(b'WAVE')
            
            # fmt子块
            wav_header.extend(b'fmt ')
            wav_header.extend(struct.pack('<I', 16))  # 子块大小
            wav_header.extend(struct.pack('<H', 1))  # 音频格式（PCM）
            wav_header.extend(struct.pack('<H', channels))  # 声道数
            wav_header.extend(struct.pack('<I', sample_rate))  # 采样率
            wav_header.extend(struct.pack('<I', sample_rate * channels * sample_width))  # 字节率
            wav_header.extend(struct.pack('<H', channels * sample_width))  # 块对齐
            wav_header.extend(struct.pack('<H', sample_width * 8))  # 位深度
            
            # data子块
            wav_header.extend(b'data')
            wav_header.extend(struct.pack('<I', data_size))  # 数据大小
            
            # 组合WAV头和音频数据
            wav_data = wav_header + audio_data
            
            logger.info(f"Created WAV format from raw audio, size: {len(wav_data)} bytes, data_size: {data_size}")
            return wav_data
        except Exception as e:
            logger.error(f"Error creating WAV format: {e}")
            return audio_data


class AsrRequestHeader:
    def __init__(self):
        self.message_type = MessageType.CLIENT_FULL_REQUEST
        self.message_type_specific_flags = MessageTypeSpecificFlags.POS_SEQUENCE
        self.serialization_type = SerializationType.JSON
        self.compression_type = CompressionType.GZIP
        self.reserved_data = bytes([0x00])

    def with_message_type(self, message_type: int) -> 'AsrRequestHeader':
        self.message_type = message_type
        return self

    def with_message_type_specific_flags(self, flags: int) -> 'AsrRequestHeader':
        self.message_type_specific_flags = flags
        return self

    def with_serialization_type(self, serialization_type: int) -> 'AsrRequestHeader':
        self.serialization_type = serialization_type
        return self

    def with_compression_type(self, compression_type: int) -> 'AsrRequestHeader':
        self.compression_type = compression_type
        return self

    def with_reserved_data(self, reserved_data: bytes) -> 'AsrRequestHeader':
        self.reserved_data = reserved_data
        return self

    def to_bytes(self) -> bytes:
        header = bytearray()
        header.append((ProtocolVersion.V1 << 4) | 1)
        header.append((self.message_type << 4) | self.message_type_specific_flags)
        header.append((self.serialization_type << 4) | self.compression_type)
        header.extend(self.reserved_data)
        return bytes(header)

    @staticmethod
    def default_header() -> 'AsrRequestHeader':
        return AsrRequestHeader()


class RequestBuilder:
    @staticmethod
    def new_auth_headers(app_key: str, access_key: str) -> Dict[str, str]:
        reqid = str(uuid.uuid4())
        return {
            "X-Api-Resource-Id": "volc.bigasr.sauc.duration",
            "X-Api-Request-Id": reqid,
            "X-Api-Access-Key": access_key,
            "X-Api-App-Key": app_key
        }

    @staticmethod
    def new_full_client_request(seq: int) -> bytes:
        header = AsrRequestHeader.default_header() \
            .with_message_type_specific_flags(MessageTypeSpecificFlags.POS_SEQUENCE)
        
        payload = {
            "user": {
                "uid": "demo_uid"
            },
            "audio": {
                "format": "wav",
                "codec": "raw",
                "rate": 16000,
                "bits": 16,
                "channel": 1
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_ddc": True,
                "show_utterances": True,
                "enable_nonstream": False
            }
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        compressed_payload = CommonUtils.gzip_compress(payload_bytes)
        payload_size = len(compressed_payload)
        
        request = bytearray()
        request.extend(header.to_bytes())
        request.extend(struct.pack('>i', seq))
        request.extend(struct.pack('>I', payload_size))
        request.extend(compressed_payload)
        
        return bytes(request)

    @staticmethod
    def new_audio_only_request(seq: int, segment: bytes, is_last: bool = False) -> bytes:
        header = AsrRequestHeader.default_header()
        if is_last:
            header.with_message_type_specific_flags(MessageTypeSpecificFlags.NEG_WITH_SEQUENCE)
            seq = -seq
        else:
            header.with_message_type_specific_flags(MessageTypeSpecificFlags.POS_SEQUENCE)
        header.with_message_type(MessageType.CLIENT_AUDIO_ONLY_REQUEST)
        
        request = bytearray()
        request.extend(header.to_bytes())
        request.extend(struct.pack('>i', seq))
        
        compressed_segment = CommonUtils.gzip_compress(segment)
        request.extend(struct.pack('>I', len(compressed_segment)))
        request.extend(compressed_segment)
        
        return bytes(request)


class AsrResponse:
    def __init__(self):
        self.code = 0
        self.event = 0
        self.is_last_package = False
        self.payload_sequence = 0
        self.payload_size = 0
        self.payload_msg = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "event": self.event,
            "is_last_package": self.is_last_package,
            "payload_sequence": self.payload_sequence,
            "payload_size": self.payload_size,
            "payload_msg": self.payload_msg
        }


class ResponseParser:
    @staticmethod
    def parse_response(msg: bytes) -> AsrResponse:
        response = AsrResponse()
        
        header_size = msg[0] & 0x0f
        message_type = msg[1] >> 4
        message_type_specific_flags = msg[1] & 0x0f
        serialization_method = msg[2] >> 4
        message_compression = msg[2] & 0x0f
        
        payload = msg[header_size*4:]
        
        # 解析message_type_specific_flags
        if message_type_specific_flags & 0x01:
            response.payload_sequence = struct.unpack('>i', payload[:4])[0]
            payload = payload[4:]
        if message_type_specific_flags & 0x02:
            response.is_last_package = True
        if message_type_specific_flags & 0x04:
            response.event = struct.unpack('>i', payload[:4])[0]
            payload = payload[4:]
            
        # 解析message_type
        if message_type == MessageType.SERVER_FULL_RESPONSE:
            response.payload_size = struct.unpack('>I', payload[:4])[0]
            payload = payload[4:]
        elif message_type == MessageType.SERVER_ERROR_RESPONSE:
            response.code = struct.unpack('>i', payload[:4])[0]
            response.payload_size = struct.unpack('>I', payload[4:8])[0]
            payload = payload[8:]
            
        if not payload:
            return response
            
        # 解压缩
        if message_compression == CompressionType.GZIP:
            try:
                payload = CommonUtils.gzip_decompress(payload)
            except Exception as e:
                logger.error(f"Failed to decompress payload: {e}")
                return response
                
        # 解析payload
        try:
            if serialization_method == SerializationType.JSON:
                response.payload_msg = json.loads(payload.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to parse payload: {e}")
            
        return response


class DoubaoASRClient:
    def __init__(self, config: ASRConfig):
        self.config = config
        self.base_url = config.base_url
        self.seq = 1
    
    def recognize(self, audio_data: bytes) -> str:
        """识别音频数据并返回文本"""
        import requests
        
        # 转换音频数据为WAV格式
        wav_data = CommonUtils.convert_to_wav(audio_data)
        
        # 构建请求URL
        url = f"{self.base_url.rstrip('/')}/audio/transcriptions"
        
        # 构建请求头
        # headers = {
        #     "Content-Type": "audio/wav"
        # }
        
        # 构建请求数据
        files = {
            "file": ("audio.wav", wav_data, "audio/wav")
        }
        print(url)
        # 发送请求
        try:
            logger.info(f"Sending ASR request to: {url}")
            response = requests.post(url, headers=headers, files=files, timeout=30)
            
            logger.info(f"ASR response status code: {response.status_code}")
            logger.info(f"ASR response content: {response.text}")
            
            # 检查响应状态
            if response.status_code != 200:
                raise ASRError(f"ASR request failed: {response.status_code}, {response.text}")
            
            # 解析响应
            try:
                result = response.json()
                # 提取识别结果
                if "text" in result:
                    return result["text"]
                elif "result" in result and "text" in result["result"]:
                    return result["result"]["text"]
                else:
                    raise ASRError(f"Invalid ASR response format: {result}")
            except json.JSONDecodeError:
                # 如果响应不是JSON格式，尝试直接返回文本
                return response.text.strip()
        except requests.RequestException as e:
            logger.error(f"ASR request error: {e}")
            raise ASRError(f"ASR request error: {str(e)}")
    
    def recognize_stream(self, audio_data: bytes) -> str:
        """实时识别音频流并返回文本"""
        # 对于本地模型，我们使用相同的实现
        return self.recognize(audio_data)
