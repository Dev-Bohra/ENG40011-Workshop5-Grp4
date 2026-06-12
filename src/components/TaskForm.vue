<template>
  <div class="task-form-wrapper">
    <form @submit.prevent="submitForm">
      <div class="mb-3">
        <label class="form-label fw-semibold small">Task Description</label>
        <input
          v-model="form.content"
          type="text"
          class="form-control"
          placeholder="e.g., Medicine reminder"
          required
        >
      </div>

      <div class="mb-3">
        <label class="form-label fw-semibold small">Time</label>
        <input
          v-model="form.time"
          type="time"
          class="form-control"
          required
        >
      </div>

      <div class="mb-4">
        <label class="form-label fw-semibold small">Frequency</label>

        <div class="btn-group w-100" role="group">
          <input
            id="once"
            v-model="form.frequency"
            type="radio"
            class="btn-check"
            value="once"
          >
          <label class="btn btn-outline-secondary btn-sm" for="once">
            One-time
          </label>

          <input
            id="daily"
            v-model="form.frequency"
            type="radio"
            class="btn-check"
            value="daily"
          >
          <label class="btn btn-outline-secondary btn-sm" for="daily">
            Daily Task
          </label>
        </div>
      </div>

      <button
        type="submit"
        class="btn w-100 py-2"
        :class="editingTask ? 'btn-warning' : 'btn-primary'"
      >
        {{ editingTask ? 'Update Task' : 'Add to Schedule' }}
      </button>

      <button
        v-if="editingTask"
        type="button"
        class="btn btn-link w-100 mt-2 text-secondary text-decoration-none"
        @click="cancelEdit"
      >
        Cancel
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  editingTask: {
    type: Object,
    default: null
  },
  selectedDate: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['add-task', 'update-task']);

const form = ref({
  content: '',
  time: '',
  frequency: 'once',
  date: props.selectedDate
});

const resetForm = () => {
  form.value = {
    content: '',
    time: '',
    frequency: 'once',
    date: props.selectedDate
  };
};

watch(
  () => props.editingTask,
  (newVal) => {
    if (newVal) {
      form.value = {
        content: newVal.content || '',
        time: newVal.time || '',
        frequency: newVal.frequency || 'once',
        date: newVal.date || props.selectedDate,
        status: newVal.status || 'Pending',
        id: newVal.id
      };
    } else {
      resetForm();
    }
  },
  { immediate: true }
);

watch(
  () => props.selectedDate,
  (newDate) => {
    if (!props.editingTask) {
      form.value.date = newDate;
    }
  }
);

const submitForm = () => {
  if (props.editingTask) {
    emit('update-task', {
      ...form.value,
      date: form.value.date || props.selectedDate
    });
  } else {
    emit('add-task', {
      ...form.value,
      date: props.selectedDate
    });
  }

  resetForm();
};

const cancelEdit = () => {
  emit('update-task', null);
  resetForm();
};
</script>

<style scoped>
.task-form-wrapper {
  width: 100%;
}
</style>