<script setup lang="ts">
defineProps<{
  inspectorOpen: boolean
  closeInspectorLabel: string
  singleColumn?: boolean
}>()

const emit = defineEmits<{
  closeInspector: []
}>()
</script>

<template>
  <div
    class="main-stage"
    :class="{
      'inspector-active': inspectorOpen,
      'single-column': singleColumn,
    }"
  >
    <button
      v-if="inspectorOpen"
      class="inspector-overlay-backdrop"
      type="button"
      :aria-label="closeInspectorLabel"
      @click="emit('closeInspector')"
    ></button>

    <slot></slot>
    <slot name="inspector"></slot>
  </div>
</template>
