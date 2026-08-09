const CompanyDashboard = {
  data() {
    return {
      profile: {}, 
      drives: [], 
      error: "", 
      loading: true,
      exporting: false, 
      exportMessage: "", downloadUrl: "", 
      pollHandle: null,
    };
  },
  async mounted() {
    await this.load();
  },
  beforeUnmount() {
    if (this.pollHandle) clearInterval(this.pollHandle);
  },
  computed: {
    upcomingDrives() { return this.drives.filter(d => d.status !== "closed"); },
    closedDrives() { return this.drives.filter(d => d.status === "closed"); },
  },
  template: `
    <div class="container">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <h3>Welcome, {{ profile.company_name }}</h3>
        <router-link to="/company/create-drive" class="btn btn-pp" v-if="profile.approval_status === 'approved'">
          <i class="bi bi-plus-lg"></i> Create Drive
        </router-link>
      </div>
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-warning" v-if="profile.approval_status === 'pending'">
        Your company registration is pending admin approval. You'll be able to create drives once approved.
      </div>
      <div class="alert alert-danger" v-if="profile.approval_status === 'rejected'">
        Your company registration was rejected by the admin.
      </div>

      <div class="card card-pp p-3 mb-4">
        <h5>Company Details</h5>
        <p class="mb-1"><b>Industry:</b> {{ profile.industry || '-' }}</p>
        <p class="mb-1"><b>Location:</b> {{ profile.location || '-' }}</p>
        <p class="mb-1"><b>HR Contact:</b> {{ profile.hr_contact || '-' }}</p>
        <p class="mb-1"><b>HR Email:</b> {{ profile.hr_email || '-' }}</p>
        <p class="mb-1"><b>Website:</b> {{ profile.website || '-' }}</p>
        <p class="mb-0"><b>Description:</b> {{ profile.description || '-' }}</p>
      </div>

      <div class="card card-pp p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center">
          <h6 class="mb-0">Export application/placement history</h6>
          <button class="btn btn-sm btn-pp" @click="startExport" :disabled="exporting">
            <i class="bi bi-download me-1"></i>{{ exporting ? 'Exporting...' : 'Export as CSV' }}
          </button>
        </div>
        <div class="alert alert-info mt-2 mb-0 py-2" v-if="exportMessage">
          {{ exportMessage }}
          <a v-if="downloadUrl" :href="downloadUrl" class="ms-2 fw-bold">Download CSV</a>
        </div>
      </div>

      <div class="card card-pp p-3 mb-4">
        <h5>Upcoming Drives</h5>
        <table class="table table-pp table-sm align-middle">
          <thead><tr><th>Sr No.</th><th>Job Title</th><th>Applicants</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="(d, i) in upcomingDrives" :key="d.id">
              <td>{{ i + 1 }}</td>
              <td>{{ d.job_title }}</td>
              <td>{{ d.applicant_count }}</td>
              <td><span class="badge" :class="'badge-' + d.status">{{ d.status }}</span></td>
              <td>
                <router-link :to="'/company/drives/' + d.id + '/applications'" class="btn btn-sm btn-outline-pp me-1"
                              v-if="d.status === 'approved'">View Applications</router-link>
                <button class="btn btn-sm btn-pp" v-if="d.status === 'approved'" @click="markComplete(d)">Mark Complete</button>
              </td>
            </tr>
            <tr v-if="!upcomingDrives.length"><td colspan="5" class="text-muted">No drives yet.</td></tr>
          </tbody>
        </table>
      </div>

      <div class="card card-pp p-3">
        <h5>Closed Drives</h5>
        <table class="table table-pp table-sm align-middle">
          <thead><tr><th>Sr No.</th><th>Job Title</th><th>Applicants</th></tr></thead>
          <tbody>
            <tr v-for="(d, i) in closedDrives" :key="d.id">
              <td>{{ i + 1 }}</td><td>{{ d.job_title }}</td><td>{{ d.applicant_count }}</td>
            </tr>
            <tr v-if="!closedDrives.length"><td colspan="3" class="text-muted">No closed drives yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  methods: {
    async load() {
      this.loading = true;
      try {
        const [profile, drives] = await Promise.all([
          Api.get("/api/company/profile"),
          Api.get("/api/company/drives"),
        ]);
        this.profile = profile; 
        this.drives = drives;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
    
    //drive end, celery impl-expp and stats checkk :)
    async markComplete(d) {
      await Api.post(`/api/company/drives/${d.id}/complete`);
      this.load(); //arekta await kore try catch kora jay but nehh
    },

    async startExport() {
      this.exporting = true;
      this.downloadUrl = "";
      this.exportMessage = "Export started, please wait..";
      try {
        const { task_id } = await Api.post("/api/company/export-csv");
        this.pollHandle = setInterval(() => this.checkStatus(task_id), 1500);
      } catch (e) {
        this.error = e.message;
        this.exporting = false;
      }
    },
    async checkStatus(taskId) {
      try {
        const res = await Api.get(`/api/company/export-status/${taskId}`);
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
