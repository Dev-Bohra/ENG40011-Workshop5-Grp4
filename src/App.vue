<template>
  <div class="container-fluid dashboard-page py-4">
    <!-- Header -->
    <header class="dashboard-header mb-4">
      <div>
        <h1 class="display-6 fw-bold mb-1">AD Care Monitoring Dashboard</h1>
        <p class="text-secondary mb-0">
          Drag-and-drop care task management with online database storage
        </p>
      </div>

      <div class="header-actions">
        <button class="btn btn-primary" @click="openAddTaskModal">
          + Add Task
        </button>

        <button class="btn btn-dark" @click="openCameraModal">
          View Camera
        </button>
      </div>
    </header>

    <!-- Fire Alert Banner -->
    <div v-if="fireAlert" class="alert alert-danger fw-bold fire-alert-banner">
      <div>
        🚨 {{ fireAlertMessage || 'FIRE DETECTED – CHECK PATIENT IMMEDIATELY' }}
      </div>

      <small v-if="fireAlertUpdatedAt" class="d-block mt-1">
        Last update: {{ formatCompletedAt(fireAlertUpdatedAt) }}
      </small>
    </div>

    <!-- Weekday Selector -->
    <div class="date-panel mb-4">
      <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h5 class="mb-1">Weekly Schedule</h5>
          <p class="text-secondary mb-0 small">
            Select a weekday and manage care tasks by dragging cards between status columns.
          </p>
        </div>

        <div class="task-count">
          {{ filteredAndSortedTasks.length }} task(s) shown
        </div>
      </div>

      <div class="d-flex gap-2 flex-wrap">
        <button
          v-for="day in weekDates"
          :key="day.fullDate"
          @click="selectedDate = day.fullDate"
          class="btn shadow-sm date-btn"
          :class="selectedDate === day.fullDate ? 'btn-primary' : 'btn-outline-primary'"
        >
          <div class="fw-bold">{{ day.weekday }}</div>
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>

    <div v-if="loading" class="alert alert-info">
      Loading tasks from online database...
    </div>

    <!-- Main Board -->
    <div class="board-section">
      <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h4 class="mb-0 text-dark">Care Task Board</h4>
          <p class="text-secondary mb-0 small">
            Tasks for {{ selectedWeekday }}
          </p>
        </div>

        <button class="btn btn-outline-secondary btn-sm" @click="refreshDashboard">
          Refresh
        </button>
      </div>

      <TaskBoard
        :tasks="filteredAndSortedTasks"
        @delete-task="handleDeleteTask"
        @edit-task="openEditTaskModal"
        @status-change="handleStatusChange"
        @view-evidence="openEvidenceModal"
      />
    </div>

    <!-- Add / Edit Task Modal -->
    <div v-if="showTaskModal" class="modal-mask">
      <div class="modal-window task-modal">
        <div class="modal-header-custom">
          <div>
            <h4 class="mb-1">
              {{ currentTask ? 'Edit Care Task' : 'Add New Care Task' }}
            </h4>
            <p class="text-secondary mb-0 small">
              Create or update a care task for the selected weekday.
            </p>
          </div>

          <button class="btn-close" @click="closeTaskModal"></button>
        </div>

        <div class="modal-body-custom">
          <TaskForm
            :selectedDate="selectedDate"
            :editingTask="currentTask"
            @add-task="handleAddTask"
            @update-task="handleUpdateTask"
          />
        </div>
      </div>
    </div>

    <!-- Evidence Modal -->
    <div v-if="showEvidenceModal" class="modal-mask">
      <div class="modal-window evidence-modal">
        <div class="modal-header-custom">
          <div>
            <h4 class="mb-1">Task Completion Evidence</h4>
            <p class="text-secondary mb-0 small">
              Evidence captured after the task was completed.
            </p>
          </div>

          <button class="btn-close" @click="closeEvidenceModal"></button>
        </div>

        <div class="modal-body-custom">
          <div v-if="selectedEvidenceTask" class="mb-3 evidence-task-info">
            <div>
              <strong>Task:</strong>
              {{ selectedEvidenceTask.content }}
            </div>

            <div>
              <strong>Time:</strong>
              {{ selectedEvidenceTask.time }}
            </div>

            <div v-if="selectedEvidenceTask.completed_by">
              <strong>Completed by:</strong>
              {{ selectedEvidenceTask.completed_by }}
            </div>

            <div v-if="selectedEvidenceTask.completed_at">
              <strong>Completed at:</strong>
              {{ formatCompletedAt(selectedEvidenceTask.completed_at) }}
            </div>
          </div>

          <div class="evidence-box">
            <img
              :src="evidenceImageUrl"
              class="evidence-image"
              alt="Task completion evidence"
              @error="handleEvidenceImageError"
            />
          </div>

          <div class="camera-note mt-3">
            <strong>Evidence interface:</strong>
            this area displays the task evidence image. If the vision algorithm uploads a photo
            and saves its URL in the database, the dashboard will show that image here.
          </div>
        </div>
      </div>
    </div>

    <!-- Remote Camera Modal -->
    <div v-if="showCameraModal" class="modal-mask">
      <div class="modal-window camera-modal">
        <div class="modal-header-custom">
          <div>
            <h4 class="mb-1">Live Camera View</h4>
            <p class="text-secondary mb-0 small">
              Live monitoring feed from the remote always-on patient care camera.
            </p>
          </div>

          <button class="btn-close" @click="closeCameraModal"></button>
        </div>

        <div class="modal-body-custom">
          <div v-if="cameraError" class="alert alert-warning">
            {{ cameraError }}
          </div>

          <div class="camera-box">
            <img
              v-if="cameraActive"
              :src="cameraStreamUrl"
              class="camera-video"
              alt="Remote camera feed"
              @error="handleCameraError"
            />

            <div v-if="!cameraActive" class="camera-placeholder">
              <div class="camera-icon">📷</div>
              <p class="mb-1">Connecting to remote camera feed...</p>
              <small>
                The camera is assumed to be always on. The dashboard only connects to the stream.
              </small>
            </div>
          </div>

          <div class="camera-note mt-3">
            <strong>Remote camera interface:</strong>
            this view connects to a video stream from another device on the same network.
            For example, an external camera connected to another laptop can be streamed to this dashboard.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import TaskForm from './components/TaskForm.vue';
import TaskBoard from './components/TaskBoard.vue';
import { supabase } from './supabase';

const tasks = ref([]);
const taskStatusRecords = ref([]);
const currentTask = ref(null);
const selectedDate = ref(new Date().toISOString().split('T')[0]);

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const showTaskModal = ref(false);

const showEvidenceModal = ref(false);
const selectedEvidenceTask = ref(null);
const evidenceImageUrl = ref('/evidence.jpg');

const showCameraModal = ref(false);
const cameraActive = ref(false);
const cameraError = ref('');

const fireAlert = ref(false);
const fireAlertMessage = ref('');
const fireAlertUpdatedAt = ref('');

let refreshTimer = null;

const cameraStreamUrl = ref('http://192.168.47.239:8080//video');

const weekDates = computed(() => {
  const dates = [];
  const now = new Date();
  const startOfWeek = new Date(now);

  startOfWeek.setDate(now.getDate() - now.getDay() + 1);

  for (let i = 0; i < 7; i++) {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + i);

    const fullDate = d.toISOString().split('T')[0];

    dates.push({
      fullDate,
      weekday: d.toLocaleDateString('en-US', { weekday: 'short' })
    });
  }

  return dates;
});

const selectedWeekday = computed(() => {
  const d = new Date(selectedDate.value);

  return d.toLocaleDateString('en-US', {
    weekday: 'long'
  });
});

const normalizeStatus = (status) => {
  if (!status) return 'Pending';

  const lower = String(status).toLowerCase();

  if (lower === 'completed') return 'Completed';
  if (lower === 'missed') return 'Missed';
  return 'Pending';
};

const normalizeFrequency = (frequency) => {
  if (!frequency) return 'once';

  const lower = String(frequency).toLowerCase();

  if (lower === 'daily') return 'daily';
  return 'once';
};

const findStatusRecord = (taskId, date) => {
  return taskStatusRecords.value.find(item => {
    return Number(item.task_id) === Number(taskId) && item.task_date === date;
  });
};

const filteredAndSortedTasks = computed(() => {
  const statusWeight = {
    Pending: 1,
    Missed: 2,
    Completed: 3
  };

  return tasks.value
    .filter(task => {
      return task.date === selectedDate.value || task.frequency === 'daily';
    })
    .map(task => {
      const statusRecord = findStatusRecord(task.id, selectedDate.value);

      return {
        ...task,
        displayDate: selectedDate.value,
        status: statusRecord
          ? normalizeStatus(statusRecord.status)
          : task.frequency === 'daily'
            ? 'Pending'
            : normalizeStatus(task.status),
        evidence_url: statusRecord?.evidence_url || '',
        completed_by: statusRecord?.completed_by || '',
        completed_at: statusRecord?.completed_at || ''
      };
    })
    .sort((a, b) => {
      const weightA = statusWeight[a.status] || 99;
      const weightB = statusWeight[b.status] || 99;

      if (weightA !== weightB) {
        return weightA - weightB;
      }

      return String(a.time || '').localeCompare(String(b.time || ''));
    });
});

const mapRowToTask = (row) => {
  return {
    id: row.id,
    content: row.content || '',
    time: row.task_time ? String(row.task_time).substring(0, 5) : '',
    date: row.task_date,
    frequency: normalizeFrequency(row.frequency),
    status: normalizeStatus(row.status),
    evidence_url: row.evidence_url || ''
  };
};

const clearMessages = () => {
  errorMessage.value = '';
  successMessage.value = '';
};

const fetchTaskStatusRecords = async () => {
  const { data, error } = await supabase
    .from('care_task_status')
    .select('*');

  if (error) {
    console.error('Failed to fetch task status records:', error);
    errorMessage.value = 'Failed to fetch daily task status records: ' + error.message;
    return;
  }

  taskStatusRecords.value = data || [];
};

const fetchTasks = async (showLoading = true) => {
  if (showLoading) {
    loading.value = true;
    clearMessages();
  }

  const { data, error } = await supabase
    .from('care_tasks')
    .select('*')
    .order('task_date', { ascending: true })
    .order('task_time', { ascending: true });

  if (error) {
    if (showLoading) {
      loading.value = false;
    }

    console.error('Failed to fetch tasks:', error);
    errorMessage.value = 'Failed to fetch tasks from Supabase: ' + error.message;
    return;
  }

  tasks.value = data.map(mapRowToTask);

  await fetchTaskStatusRecords();

  if (showLoading) {
    loading.value = false;
  }
};

const fetchFireAlert = async () => {
  const { data, error } = await supabase
    .from('fire_alert_status')
    .select('*')
    .eq('id', 1)
    .single();

  if (error) {
    console.error('Failed to fetch fire alert:', error.message);
    return;
  }

  if (data) {
    fireAlert.value = Boolean(data.fire_alert);
    fireAlertMessage.value = data.message || '';
    fireAlertUpdatedAt.value = data.updated_at || '';
  }
};

const refreshDashboard = async () => {
  await fetchTasks(true);
  await fetchFireAlert();
};

const silentRefreshDashboard = async () => {
  await fetchTasks(false);
  await fetchFireAlert();
};

const handleAddTask = async (newTask) => {
  clearMessages();

  const taskToInsert = {
    content: newTask.content,
    task_time: newTask.time,
    task_date: newTask.date || selectedDate.value,
    frequency: newTask.frequency || 'once',
    status: 'Pending'
  };

  const { data, error } = await supabase
    .from('care_tasks')
    .insert(taskToInsert)
    .select();

  if (error) {
    console.error('Failed to add task:', error);
    errorMessage.value = 'Failed to add task: ' + error.message;
    return;
  }

  console.log('Inserted task:', data);

  closeTaskModal();

  selectedDate.value = taskToInsert.task_date;

  await refreshDashboard();

  successMessage.value = 'Task added successfully.';
};

const handleUpdateTask = async (updatedTask) => {
  if (!updatedTask) {
    closeTaskModal();
    return;
  }

  clearMessages();

  const taskToUpdate = {
    content: updatedTask.content,
    task_time: updatedTask.time,
    task_date: updatedTask.date || selectedDate.value,
    frequency: updatedTask.frequency || 'once',
    status: normalizeStatus(updatedTask.status)
  };

  const { error } = await supabase
    .from('care_tasks')
    .update(taskToUpdate)
    .eq('id', updatedTask.id);

  if (error) {
    console.error('Failed to update task:', error);
    errorMessage.value = 'Failed to update task: ' + error.message;
    return;
  }

  closeTaskModal();

  selectedDate.value = taskToUpdate.task_date;

  await refreshDashboard();

  successMessage.value = 'Task updated successfully.';
};

const handleDeleteTask = async (id) => {
  if (!confirm('Delete this task?')) return;

  clearMessages();

  const { error } = await supabase
    .from('care_tasks')
    .delete()
    .eq('id', id);

  if (error) {
    console.error('Failed to delete task:', error);
    errorMessage.value = 'Failed to delete task: ' + error.message;
    return;
  }

  await refreshDashboard();

  successMessage.value = 'Task deleted successfully.';
};

const handleStatusChange = async (id, newStatus) => {
  clearMessages();

  const normalizedStatus = normalizeStatus(newStatus);

  const task = tasks.value.find(item => Number(item.id) === Number(id));

  if (!task) {
    errorMessage.value = 'Task not found.';
    return;
  }

  if (task.frequency === 'daily') {
    const { error } = await supabase
      .from('care_task_status')
      .upsert(
        {
          task_id: id,
          task_date: selectedDate.value,
          status: normalizedStatus,
          completed_by: normalizedStatus === 'Completed' ? 'manual' : null,
          completed_at: normalizedStatus === 'Completed' ? new Date().toISOString() : null
        },
        {
          onConflict: 'task_id,task_date'
        }
      );

    if (error) {
      console.error('Failed to update daily task status:', error);
      errorMessage.value = 'Failed to update daily task status: ' + error.message;
      return;
    }

    await refreshDashboard();
    return;
  }

  const { error } = await supabase
    .from('care_tasks')
    .update({
      status: normalizedStatus
    })
    .eq('id', id);

  if (error) {
    console.error('Failed to update task status:', error);
    errorMessage.value = 'Failed to update task status: ' + error.message;
    return;
  }

  await refreshDashboard();
};

const openAddTaskModal = () => {
  currentTask.value = null;
  showTaskModal.value = true;
};

const openEditTaskModal = (task) => {
  currentTask.value = { ...task };
  showTaskModal.value = true;
};

const closeTaskModal = () => {
  currentTask.value = null;
  showTaskModal.value = false;
};

const openEvidenceModal = (task) => {
  selectedEvidenceTask.value = task;

  if (task.evidence_url) {
    evidenceImageUrl.value = task.evidence_url;
  } else {
    evidenceImageUrl.value = '/evidence.jpg';
  }

  showEvidenceModal.value = true;
};

const closeEvidenceModal = () => {
  selectedEvidenceTask.value = null;
  evidenceImageUrl.value = '/evidence.jpg';
  showEvidenceModal.value = false;
};

const handleEvidenceImageError = () => {
  evidenceImageUrl.value = '/evidence.jpg';
};

const formatCompletedAt = (completedAt) => {
  if (!completedAt) return '';

  const d = new Date(completedAt);

  if (Number.isNaN(d.getTime())) {
    return completedAt;
  }

  return d.toLocaleString();
};

const openCameraModal = () => {
  cameraError.value = '';
  cameraActive.value = true;
  showCameraModal.value = true;
};

const closeCameraModal = () => {
  cameraActive.value = false;
  showCameraModal.value = false;
};

const handleCameraError = () => {
  cameraError.value = 'Failed to load remote camera stream. Please check the camera server URL and network connection.';
  cameraActive.value = false;
};

onMounted(() => {
  refreshDashboard();

  refreshTimer = setInterval(() => {
    silentRefreshDashboard();
  }, 3000);
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: #f4f7fb;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.fire-alert-banner {
  border-radius: 14px;
  font-size: 1rem;
  box-shadow: 0 6px 18px rgba(220, 53, 69, 0.18);
}

.date-panel {
  background: white;
  border-radius: 18px;
  padding: 1.2rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
}

.date-btn {
  min-width: 80px;
  border-radius: 12px;
}

.task-count {
  background: #eef2ff;
  color: #0d6efd;
  border-radius: 999px;
  padding: 0.45rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.board-section {
  background: white;
  border-radius: 18px;
  padding: 1.2rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
  padding: 1rem;
}

.modal-window {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
}

.task-modal {
  max-width: 520px;
}

.evidence-modal {
  max-width: 780px;
}

.camera-modal {
  max-width: 900px;
}

.modal-header-custom {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.modal-body-custom {
  padding: 1.5rem;
}

.evidence-task-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: #495057;
}

.evidence-box {
  background: #111827;
  border-radius: 16px;
  min-height: 360px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.evidence-image {
  max-width: 100%;
  max-height: 480px;
  object-fit: contain;
  display: block;
}

.camera-box {
  position: relative;
  background: #111827;
  border-radius: 16px;
  min-height: 420px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.camera-video {
  width: 100%;
  height: 420px;
  object-fit: cover;
  display: block;
}

.camera-placeholder {
  position: absolute;
  color: #d1d5db;
  text-align: center;
  padding: 1rem;
}

.camera-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
}

.camera-note {
  background: #f8f9fa;
  border-left: 4px solid #0d6efd;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  color: #495057;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .dashboard-header {
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
  }

  .camera-box {
    min-height: 300px;
  }

  .camera-video {
    height: 300px;
  }

  .evidence-box {
    min-height: 260px;
  }
}
</style>