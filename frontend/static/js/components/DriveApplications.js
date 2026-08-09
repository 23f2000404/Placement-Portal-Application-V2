const DriveApplications = {
  data() {
    return {
      applications: [], selected: null,
      newStatus: "applied", remark: "", feedback: "",
      interviewDate: "", interviewMode: "Online",
      position: "", salary: "", joiningDate: "",
      error: "", success: "", loading: true,
    };
  },
  async mounted() {
    await this.load();
  },
  template: `
    <div class="container">
      <h3 class="mb-3">Update Applications for the Drive</h3>
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>

      <div class="card card-pp p-3 mb-4" v-if="!selected">
        <h5>Received Applications</h5>
        <table class="table table-pp table-sm align-middle">
          <thead><tr><th>Student</th><th>Status</th><th>Interview</th><th></th></tr></thead>
          <tbody>
            <tr v-for="a in applications" :key="a.id">
              <td>{{ a.student_name }}</td>
              <td><span class="badge" :class="'badge-' + a.status">{{ a.status }}</span></td>
              <td class="small text-muted">   
                {# Interview date looks weird so I sliced it up manually to get YYYY-MM-DD HH:MM format teehee :D #}
                <template v-if="a.interview_date">{{ a.interview_date.slice(0,16).replace('T',' ') }} ({{ a.interview_mode }})</template>
                <template v-else>-</template>
              </td>
              <td><button class="btn btn-sm btn-outline-pp" @click="openReview(a)">Review Application</button></td>
            </tr>
            <tr v-if="!applications.length"><td colspan="4" class="text-muted">No applications received yet.</td></tr>
          </tbody>
        </table>
        <router-link to="/company" class="btn btn-outline-pp mt-2" style="width: fit-content;">Go Back</router-link>
      </div>

      <div class="card card-pp p-4" v-else style="max-width: 620px;">
        <h5>Student Application</h5>
        <p class="mb-1"><b>Student Name:</b> {{ selected.student_name }}</p>
        <p class="mb-1"><b>Drive:</b> {{ selected.drive_title }}</p>
        <p class="mb-3"><b>Applied on:</b> {{ (selected.application_date || '').slice(0,10) }}</p>
        <a v-if="selected.resume_filename" :href="'/api/company/applications/' + selected.id + '/resume'"
          class="btn btn-sm btn-outline-pp mb-2" target="_blank">View Resume</a>
        <p v-else class="small text-muted">No resume uploaded.</p>
        
        <div class="mb-3">
          <label class="form-label">Update Status</label>
          <select v-model="newStatus" class="form-select">
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="interview">Interview</option>
            <option value="offer">Offer</option>
            <option value="placed">Placed</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <div class="mb-3">
          <label class="form-label">Remark (optional)</label>
          <input v-model="remark" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Feedback for student (optional)</label>
          <textarea v-model="feedback" class="form-control" rows="2"></textarea>
        </div>

        <div class="d-flex gap-2 mb-4">
          <button class="btn btn-pp" @click="saveStatus">Save Status</button>
          <button class="btn btn-outline-pp" @click="selected = null">Back</button>
        </div>

        <hr>
        <h6>Schedule Interview</h6>
        <div class="row g-2 mb-2">
          <div class="col-md-7">
            <input v-model="interviewDate" type="datetime-local" class="form-control" />
          </div>
          <div class="col-md-5">
            <select v-model="interviewMode" class="form-select">
              <option value="Online">Online</option>
              <option value="In-person">In-person</option>
              <option value="Telephonic">Telephonic</option>
            </select>
          </div>
        </div>
        <button class="btn btn-sm btn-outline-pp mb-4" @click="scheduleInterview">Schedule Interview</button>

        <hr>
        <h6>Placement Details</h6>
        <div class="row g-2">
          <div class="col-md-6"><input v-model="position" class="form-control" placeholder="Position" /></div>
          <div class="col-md-3"><input v-model="salary" type="number" class="form-control" placeholder="Salary" /></div>
          <div class="col-md-3"><input v-model="joiningDate" type="date" class="form-control" /></div>
        </div>
      </div>
    </div>
  `,
  methods: {
    async load() {
      this.loading = true;
      try {
        this.applications = await Api.get(`/api/company/drives/${this.$route.params.id}/applications`);
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
    openReview(a) {
      this.selected = a;
      this.newStatus = a.status;
      this.remark = a.remark || "";
      this.feedback = a.feedback || "";
      this.interviewDate = ""; this.interviewMode = a.interview_mode || "Online";
      this.position = ""; this.salary = ""; this.joiningDate = "";
      this.error = ""; this.success = "";
    },
    async saveStatus() {
      this.error = ""; this.success = "";
      try {
        await Api.post(`/api/company/applications/${this.selected.id}/status`, {
          status: this.newStatus, remark: this.remark, feedback: this.feedback,
          position: this.position || undefined,
          salary: this.salary || undefined,
          joining_date: this.joiningDate || undefined,
        });
        this.success = "Status updated.";
        await this.load();
        this.selected = null;
      } catch (e) {
        this.error = e.message;
      }
    },
    async scheduleInterview() {
      this.error = ""; this.success = "";
      if (!this.interviewDate) {
        this.error = "Pick an interview date/time first.";
        return;
      }
      try {
        await Api.post(`/api/company/applications/${this.selected.id}/schedule-interview`, {
          interview_date: this.interviewDate,
          interview_mode: this.interviewMode,
        });
        this.success = "Interview scheduled.";
        this.selected = null;
        this.load();
      } catch (e) {
        this.error = e.message;
      }
    },
  },
};
