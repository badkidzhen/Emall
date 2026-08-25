<template>
  <div class="image-upload">
    <el-image v-if="modelValue" class="image-preview" :src="modelValue" fit="cover" :preview-src-list="[modelValue]" />
    <div v-else class="image-empty">暂无图片</div>
    <div class="image-actions">
      <el-upload :show-file-list="false" :http-request="handleUpload" accept="image/png,image/jpeg,image/webp,image/gif">
        <el-button :loading="loading">上传图片</el-button>
      </el-upload>
      <el-button v-if="modelValue" text type="danger" @click="$emit('update:modelValue', '')">清除</el-button>
    </div>
    <el-input :model-value="modelValue" placeholder="图片 URL" @input="$emit('update:modelValue', $event)" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { uploadImage } from "../utils/upload";

defineProps({
  modelValue: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["update:modelValue"]);
const loading = ref(false);

async function handleUpload(options) {
  loading.value = true;
  try {
    const data = await uploadImage(options.file);
    emit("update:modelValue", data.url);
    ElMessage.success("图片上传成功");
    options.onSuccess?.(data);
  } catch (error) {
    options.onError?.(error);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.image-upload {
  width: 100%;
  display: grid;
  gap: 10px;
}

.image-preview,
.image-empty {
  width: 180px;
  height: 120px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f8fafc;
}

.image-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 13px;
}

.image-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
