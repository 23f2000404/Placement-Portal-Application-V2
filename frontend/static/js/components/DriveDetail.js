const DriveDetail = {
  data() {
    return { drive: null, error: "", success: "" };
  },
  async mounted() {
    await this.load();
  },
  template: `
    <div class="container" style="max-width: 640px;">
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>
      <div class="card card-pp p-4" v-if="drive">
        <h4>{{ drive.job_title }}</h4>
        <p class="text-muted">{{ drive.company_name }}</p>
        <p><b>Job Description</b><br>{{ drive.job_description || 'N/A' }}</p>
        <p><b>Skills Required:</b> {{ drive.skills_required || 'N/A' }}</p>
        <p><b>Experience:</b> {{ drive.experience_required || 'N/A' }}</p>
        <p><b>Benefits:</b> {{ drive.benefits || 'N/A' }}</p>
        <p><b>Eligibility</b><br>
          Branch: {{ drive.eligibility_branch }} &middot;
          Min CGPA: {{ drive.eligibility_cgpa }} &middot;
          Year: {{ drive.eligibility_year || 'Any' }}
        </p>
        <p><b>Salary:</b> {{ drive.salary || 'N/A' }}</p>
        <p><b>Location:</b> {{ drive.location || 'N/A' }}</p>
        <p><b>Application Deadline:</b> {{ drive.application_deadline }}</p>

        <div class="d-flex gap-2">
          <button class="btn btn-pp" @click="apply" v-if="drive.status === 'approved' && !drive.applied">Apply</button>
          <span class="badge badge-applied align-self-center" v-else-if="drive.applied">Applied</span>
          <button class="btn btn-outline-pp" @click="$router.back()">Go Back</button>
        </div>
      </div>
    </div>
  `,
  methods: {
    async load() {
      try {
        this.drive = await Api.get(`/api/student/drives/${this.$route.params.id}`);
      } catch (e) {
        this.error = e.message;
      }
    },
    async apply() {
      this.error = ""; this.success = "";
      try {
        await Api.post(`/api/student/drives/${this.drive.id}/apply`);
        this.success = "Applied successfully!";
        this.drive.applied = true;
      } catch (e) {
        this.error = e.message;
      }
    },
  },
};
