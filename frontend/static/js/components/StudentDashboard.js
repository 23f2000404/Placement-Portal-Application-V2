const StudentDashboard = {
  data() {
    return {
      drives: [], applications: [], q: "", eligibleOnly: false,
      error: "", success: "", loading: true,
    };
  },
  async mounted() {
    await this.load();
  },
  computed: {
    appliedDriveIds() { return new Set(this.applications.map(a => a.drive_id)); },
  },
  template: `
    <div class="container">
      <h3 class="mb-3">Approved Placement Drives</h3>
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>

      <div class="card card-pp p-3 mb-4">
        <form class="row g-2 align-items-center" @submit.prevent="load">
          <div class="col-md-6">
            <input v-model="q" class="form-control" placeholder="Search by job title, company, or skills..." />
          </div>
          <div class="col-md-4 form-check ms-2">
            <input v-model="eligibleOnly" class="form-check-input" type="checkbox" id="eligOnly">
            <label class="form-check-label" for="eligOnly">Only show drives I'm eligible for</label>
          </div>
          <div class="col-md-1">
            <button class="btn btn-pp">Search</button>
          </div>
        </form>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-md-6 col-lg-4" v-for="d in drives" :key="d.id">
          <div class="card card-pp p-3 h-100">
            <h6>{{ d.job_title }}</h6>
            <p class="mb-1 text-muted small">{{ d.company_name }} &middot; {{ d.location || 'N/A' }}</p>
            <p class="mb-1 small" v-if="d.skills_required">Skills: {{ d.skills_required }}</p>
            <p class="mb-1 small">Deadline: {{ d.application_deadline }}</p>
            <p class="mb-2 small">Salary: {{ d.salary || 'N/A' }}</p>
            <div class="d-flex gap-2 mt-auto">
              <router-link :to="'/student/drives/' + d.id" class="btn btn-sm btn-outline-pp">View Details</router-link>
              <button class="btn btn-sm btn-pp" v-if="!appliedDriveIds.has(d.id)" @click="apply(d)">Apply</button>
              <span class="badge badge-applied align-self-center" v-else>Applied</span>
            </div>
          </div>
        </div>
        <div class="col-12 text-muted" v-if="!drives.length">No drives match your filters right now.</div>
      </div>

      <div class="card card-pp p-3">
        <h5>My Applied Drives</h5>
        <table class="table table-pp table-sm align-middle">
          <thead><tr><th>Drive</th><th>Company</th><th>Date</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="a in applications" :key="a.id">
              <td>{{ a.drive_title }}</td>
              <td>{{ a.company_name }}</td>
              <td>{{ (a.application_date || '').slice(0,10) }}</td>
              <td><span class="badge" :class="'badge-' + a.status">{{ a.status }}</span></td>
            </tr>
            <tr v-if="!applications.length"><td colspan="4" class="text-muted">You haven't applied to any drives yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  methods: {
    async load() {
      this.loading = true;
      try {
        const params = new URLSearchParams();
        if (this.q) params.set("q", this.q);
        if (this.eligibleOnly) params.set("eligible_only", "true");
        const [drives, applications] = await Promise.all([
          Api.get("/api/student/drives?" + params.toString()),
          Api.get("/api/student/applications"),
        ]);
        this.drives = drives; this.applications = applications;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
    async apply(d) {
      this.error = ""; this.success = "";
      try {
        await Api.post(`/api/student/drives/${d.id}/apply`);
        this.success = `Applied to ${d.job_title} successfully.`;
        this.load(); // reloading so the Applied badge appears immediately >:D
      } catch (e) {
        this.error = e.message;
      }
    },
  },
};
