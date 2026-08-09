const CreateDrive = {
  data() {
    return {
      job_title: "", job_description: "", skills_required: "", experience_required: "", benefits: "",
      eligibility_branch: "Any", eligibility_cgpa: "", eligibility_year: "", 
      salary: "", location: "", application_deadline: "", error: "", success: "", loading: false,
    };
  },
  template: `
    <div class="container" style="max-width: 640px;">
      <h3 class="mb-3">Create a Drive</h3>
      <div class="card card-pp p-4">
        <div class="alert alert-danger" v-if="error">{{ error }}</div>
        <div class="alert alert-success" v-if="success">{{ success }}</div>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Job Title</label>
            <input v-model="job_title" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Job Description</label>
            <textarea v-model="job_description" class="form-control" rows="3"></textarea>
          </div>
          <div class="row">
            <div class="col mb-3"><label class="form-label">Skills Required</label>
              <input v-model="skills_required" class="form-control" placeholder="e.g. Python, SQL" /></div>
            <div class="col mb-3"><label class="form-label">Experience</label>
              <input v-model="experience_required" class="form-control" placeholder="e.g. Fresher / 0-1 yrs" /></div>
          </div>          
          <div class="mb-3">
            <label class="form-label">Benefits</label>
            <input v-model="benefits" class="form-control" placeholder="e.g. Health insurance, relocation" />
          </div>
          <div class="mb-3">
            <label class="form-label">Eligibility Criteria</label>
            <div class="row g-2">
              <div class="col"><input v-model="eligibility_branch" class="form-control" placeholder="Branch (or 'Any')" /></div>
              <div class="col"><input v-model="eligibility_cgpa" type="number" step="0.1" class="form-control" placeholder="Min CGPA" /></div>
              <div class="col"><input v-model="eligibility_year" type="number" class="form-control" placeholder="Grad Year" /></div>
            </div>
          </div>
          <div class="row">
            <div class="col mb-3"><label class="form-label">Salary</label>
              <input v-model="salary" type="number" class="form-control" /></div>
            <div class="col mb-3"><label class="form-label">Location</label>
              <input v-model="location" class="form-control" /></div>
          </div>
          <div class="mb-3">
            <label class="form-label">Application Deadline</label>
            <input v-model="application_deadline" type="date" class="form-control" required />
          </div>
          <button class="btn btn-pp" :disabled="loading">{{ loading ? 'Saving...' : 'Save' }}</button>
          <router-link to="/company" class="btn btn-outline-pp ms-2">Go Back</router-link>
        </form>
      </div>
    </div>
  `,
  methods: {
    async submit() {
      this.error = ""; this.success = ""; this.loading = true;
      try {
        await Api.post("/api/company/drives", {
          job_title: this.job_title,
          job_description: this.job_description,
          skills_required: this.skills_required, 
          experience_required: this.experience_required,
          benefits: this.benefits,
          eligibility_branch: this.eligibility_branch, 
          eligibility_cgpa: this.eligibility_cgpa,
          eligibility_year: this.eligibility_year, 
          salary: this.salary,
          location: this.location, 
          application_deadline: this.application_deadline,
        });
        this.success = "Drive created. Admin's approval is pending..";
        setTimeout(() => this.$router.push("/company"), 900);
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
