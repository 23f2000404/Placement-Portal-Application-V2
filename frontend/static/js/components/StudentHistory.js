const StudentHistory = {
  data() {
    return {
      history: [], 
      error: "", exporting: false, exportMessage: "", downloadUrl: "", 
      pollHandle: null,
    };
  },
  async mounted() {
    await this.load();
  },
  beforeUnmount() {
    if (this.pollHandle) clearInterval(this.pollHandle);
  },
  template: `
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>Placement Application History</h3>
        <button class="btn btn-pp" @click="startExport" :disabled="exporting">
          <i class="bi bi-download me-1"></i> {{ exporting ? 'Exporting...' : 'Export as CSV' }}
        </button>
      </div>
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-info" v-if="exportMessage">
        {{ exportMessage }}
        <a v-if="downloadUrl" :href="downloadUrl" class="ms-2 fw-bold">Download CSV</a>
      </div>

      <div class="card card-pp p-3">
        <table class="table table-pp table-sm align-middle">
          <thead><tr><th>Drive No.</th><th>Company</th><th>Job Title</th><th>Result</th><th>Interview</th><th>Applied On</th><th></th></tr></thead>
          <tbody>
            <tr v-for="(a, i) in history" :key="a.id">
              <td>{{ i + 1 }}</td>
              <td>{{ a.company_name }}</td>
              <td>{{ a.drive_title }}</td>
              <td><span class="badge" :class="'badge-' + a.status">{{ a.status }}</span></td>
              <td class="small text-muted">
                <template v-if="a.interview_date">{{ a.interview_date.slice(0,16).replace('T',' ') }}</template>
                <template v-else>-</template>
              </td>
              <td>{{ (a.application_date || '').slice(0,10) }}</td>
              <td>
                <a v-if="a.status === 'offer' || a.status === 'placed'"
                   :href="'/api/student/offer-letter/' + a.id" class="btn btn-sm btn-outline-pp">
                  {{ a.status === 'placed' ? 'Placement Confirmation' : 'Offer Letter' }}
                </a>
              </td>
            </tr>
            <tr v-if="!history.length"><td colspan="7" class="text-muted">No application history yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  methods: {
    async load() {
      try {
        this.history = await Api.get("/api/student/history");
      } catch (e) {
        this.error = e.message;
      }
    },
    async startExport() { //next celery part is added.. same thing as I've done in company part of app
      this.exporting = true;
      this.downloadUrl = "";
      this.exportMessage = "Export started, please wait...";
      try {
        const { task_id } = await Api.post("/api/student/export-csv");
        this.pollHandle = setInterval(() => this.checkStatus(task_id), 1500);
      } catch (e) {
        this.error = e.message;
        this.exporting = false;
      }
    },
    async checkStatus(taskId) {
      try {
        const res = await Api.get(`/api/student/export-status/${taskId}`);

        if (res.state === "SUCCESS") {
          clearInterval(this.pollHandle);
          this.exporting = false;
          this.exportMessage = "Your export is ready!";

          this.downloadUrl = res.result.download_url;
        } else if (res.state === "FAILURE") {
          clearInterval(this.pollHandle);

          this.exporting = false;
          this.error = "Export failed: " + res.error;
        }
      } catch (e) {
        clearInterval(this.pollHandle);
        this.exporting = false;
        this.error = e.message;
      }
    },
  },
};
