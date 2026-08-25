<template>
  <el-tag :type="meta.type" effect="light">{{ meta.label }}</el-tag>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  value: {
    type: [String, Number, Boolean],
    default: ""
  },
  map: {
    type: Object,
    default: () => ({})
  }
});

const meta = computed(() => {
  if (typeof props.value === "boolean") {
    return props.value ? { label: "是", type: "success" } : { label: "否", type: "info" };
  }
  return props.map[props.value] || { label: props.value || "-", type: "info" };
});
</script>
