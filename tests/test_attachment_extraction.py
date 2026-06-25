import unittest
import zipfile
from io import BytesIO

from app.api import MAX_EXTRACTED_ATTACHMENT_CHARS, _attachment_inline_data, extract_attachment_text


def _zip_bytes(files: dict[str, str]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class AttachmentExtractionTest(unittest.TestCase):
    def test_extracts_pptx_slide_text(self) -> None:
        pptx_bytes = _zip_bytes(
            {
                "ppt/slides/slide1.xml": (
                    '<p:sld xmlns:p="p" xmlns:a="a">'
                    "<a:t>Quality MRB workflow</a:t>"
                    "<a:t>Owner and closure evidence</a:t>"
                    "</p:sld>"
                ),
                "ppt/slides/slide2.xml": (
                    '<p:sld xmlns:p="p" xmlns:a="a">'
                    "<a:t>CAPA aging dashboard</a:t>"
                    "</p:sld>"
                ),
            }
        )

        result = extract_attachment_text("quality-flow.pptx", pptx_bytes)

        self.assertEqual(result["filename"], "quality-flow.pptx")
        self.assertEqual(result["kind"], "presentation")
        self.assertFalse(result["truncated"])
        self.assertIn("Quality MRB workflow", result["text"])
        self.assertIn("Owner and closure evidence", result["text"])
        self.assertIn("CAPA aging dashboard", result["text"])

    def test_extracts_pptx_chart_xml_text(self) -> None:
        pptx_bytes = _zip_bytes(
            {
                "ppt/charts/chart1.xml": (
                    '<c:chartSpace xmlns:c="c">'
                    "<c:v>Yield</c:v>"
                    "<c:v>Week 24</c:v>"
                    "<c:v>98.5%</c:v>"
                    "</c:chartSpace>"
                ),
            }
        )

        result = extract_attachment_text("chart-heavy.pptx", pptx_bytes)

        self.assertIn("Yield", result["text"])
        self.assertIn("Week 24", result["text"])
        self.assertIn("98.5%", result["text"])

    def test_extracts_pptx_embedded_images_for_multimodal(self) -> None:
        pptx_bytes = _zip_bytes(
            {
                "ppt/slides/slide1.xml": "<p:sld />",
                "ppt/media/image1.png": b"\x89PNG\r\n\x1a\n".decode("latin1"),
                "ppt/media/image2.jpg": "\xff\xd8\xff\xd9",
            }
        )

        inline_data = _attachment_inline_data("visual.pptx", pptx_bytes)

        self.assertEqual(len(inline_data), 2)
        self.assertEqual(inline_data[0]["mime_type"], "image/png")
        self.assertEqual(inline_data[1]["mime_type"], "image/jpeg")

    def test_truncates_long_text_attachment(self) -> None:
        long_text = "A" * (MAX_EXTRACTED_ATTACHMENT_CHARS + 100)

        result = extract_attachment_text("notes.txt", long_text.encode("utf-8"))

        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["text"]), MAX_EXTRACTED_ATTACHMENT_CHARS)

    def test_rejects_unsupported_attachment_type(self) -> None:
        with self.assertRaises(ValueError):
            extract_attachment_text("slides.ppt", b"legacy binary ppt")


if __name__ == "__main__":
    unittest.main()
