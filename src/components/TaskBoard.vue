<template>
  <div class="row g-4">
    <div
      v-for="column in columns"
      :key="column.status"
      class="col-md-4"
    >
      <div class="card board-column h-100">
        <div class="card-header column-header" :class="column.headerClass">
          <div>
            <h5 class="mb-0">{{ column.title }}</h5>
            <small>{{ column.description }}</small>
          </div>

          <span class="badge bg-light text-dark">
            {{ tasksByStatus[column.status].length }}
          </span>
        </div>

        <draggable
          class="card-body task-drop-zone"
          :list="tasksByStatus[column.status]"
          group="care-tasks"
          item-key="id"
          @change="event => handleDrop(event, column.status)"
        >
          <div
            v-for="element in tasksByStatus[column.status]"
            :key="element.id"
            class="task-card mb-3"
          >
            <div class="d-flex justify-content-between align-items-start gap-2">
              <div>
                <h6 class="mb-1 task-title">
                  {{ element.content || 'Untitled task' }}
                </h6>

                <small class="text-muted">
                  Time: {{ element.time }}
                </small>
              </div>

              <span class="badge" :class="statusClass(element.status)">
                {{ normalizeStatus(element.status) }}
              </span>
            </div>

            <div class="task-meta mt-3">
              <span>
                Frequency:
                <strong>{{ frequencyLabel(element.frequency) }}</strong>
              </span>
            </div>

            <div class="mt-3 d-flex gap-2 flex-wrap">
              <button
                class="btn btn-sm btn-outline-primary"
                @click="$emit('edit-task', element)"
              >
                Edit
              </button>

              <button
                class="btn btn-sm btn-outline-danger"
                @click="$emit('delete-task', element.id)"
              >
                Delete
              </button>

              <button
                v-if="normalizeStatus(element.status) === 'Completed'"
                class="btn btn-sm btn-outline-success"
                @click="$emit('view-evidence', element)"
              >
                View Evidence
              </button>
            </div>
          </div>

          <div
            v-if="tasksByStatus[column.status].length === 0"
            class="empty-zone"
          >
            Drag task here
          </div>
        </draggable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { VueDraggableNext as draggable } from 'vue-draggable-next';

const props = defineProps({
  tasks: {
    type: Array,
    required: true
  }
});

const emit = defineEmits([
  'status-change',
  'edit-task',
  'delete-task',
  'view-evidence'
]);

const columns = [
  {
    title: 'Pending',
    status: 'Pending',
    description: 'Tasks waiting for action',
    headerClass: 'pending-header'
  },
  {
    title: 'Missed',
    status: 'Missed',
    description: 'Tasks requiring attention',
    headerClass: 'missed-header'
  },
  {
    title: 'Completed',
    status: 'Completed',
    description: 'Finished care tasks',
    headerClass: 'completed-header'
  }
];

const normalizeStatus = (status) => {
  if (!status) return 'Pending';

  const lower = String(status).toLowerCase();

  if (lower === 'completed') return 'Completed';
  if (lower === 'missed') return 'Missed';
  return 'Pending';
};

const frequencyLabel = (frequency) => {
  if (String(frequency).toLowerCase() === 'daily') {
    return 'Daily';
  }

  return 'One-time';
};

const tasksByStatus = computed(() => {
  return {
    Pending: props.tasks.filter(task => normalizeStatus(task.status) === 'Pending'),
    Missed: props.tasks.filter(task => normalizeStatus(task.status) === 'Missed'),
    Completed: props.tasks.filter(task => normalizeStatus(task.status) === 'Completed')
  };
});

const handleDrop = (event, newStatus) => {
  if (!event.added) return;

  const movedTask = event.added.element;

  if (normalizeStatus(movedTask.status) !== newStatus) {
    emit('status-change', movedTask.id, newStatus);
  }
};

const statusClass = (status) => {
  const normalized = normalizeStatus(status);

  if (normalized === 'Completed') return 'bg-success';
  if (normalized === 'Missed') return 'bg-danger';
  return 'bg-warning text-dark';
};
</script>

<style scoped>
.board-column {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
}

.column-header {
  min-height: 86px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: none;
  color: white;
}

.pending-header {
  background: linear-gradient(135deg, #f59f00, #ffc107);
}

.missed-header {
  background: linear-gradient(135deg, #dc3545, #ff6b6b);
}

.completed-header {
  background: linear-gradient(135deg, #198754, #51cf66);
}

.task-drop-zone {
  min-height: 460px;
  background: #f8f9fa;
  padding: 1rem;
}

.task-card {
  padding: 16px;
  border-radius: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: grab;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.task-card:active {
  cursor: grabbing;
}

.task-title {
  line-height: 1.4;
}

.task-meta {
  font-size: 0.85rem;
  color: #6c757d;
  background: #f1f3f5;
  border-radius: 10px;
  padding: 0.5rem 0.7rem;
}

.empty-zone {
  border: 2px dashed #ced4da;
  border-radius: 14px;
  padding: 1.5rem;
  text-align: center;
  color: #adb5bd;
  background: white;
}
</style>