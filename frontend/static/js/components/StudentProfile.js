const StudentProfile = {
  data() {
    return { profile: {}, resumeFile: null, 
    error: "", success: "", loading: true };
  },
  async mounted() {
    await this.load();
  },
  template: `
    <div class="container" style="max-width: 560px;">
      <h3 class="mb-3">Edit Profile</h3>
      <div class="alert alert-danger" v-if="error">{{ error }}</div>
      <div class="alert alert-success" v-if="success">{{ success }}</div>
      <div class="card card-pp p-4">
        <form @submit.prevent="save">
          <div class="mb-3"><label class="form-label">Name</label>
            <input v-model="profile.name" class="form-control" required /></div>
          <div class="row">
            <div class="col mb-3"><label class="form-label">Department</label>
              <input v-model="profile.department" class="form-control" /></div>
            <div class="col mb-3"><label class="form-label">CGPA</label>
              <input v-model="profile.cgpa" type="number" step="0.01" class="form-control" /></div>
          </div>
          <div class="mb-3"><label class="form-label">Skills</label>
            <input v-model="profile.skills" class="form-control" placeholder="e.g. Python, React, SQL" /></div>
          <div class="row">
            <div class="col mb-3"><label class="form-label">Graduation Year</label>
              <input v-model="profile.year" type="number" class="form-control" /></div>
            <div class="col mb-3"><label class="form-label">Phone</label>
              <input v-model="profile.phone" class="form-control" /></div>
          </div>
          <button class="btn btn-pp">Save Profile</button>
        </form>

        <hr>
        <h6>Resume</h6>
        <p class="small text-muted mb-2">Current: {{ profile.resume_filename || 'No resume uploaded yet.' }}</p>
        <input type="file" class="form-control mb-2" @change="onFileChange" />
        <button class="btn btn-outline-pp" @click="uploadResume" :disabled="!resumeFile">Upload Resume</button>
      </div>
    </div>
  `,
  methods: {
    async load() {
      this.loading = true;
      try {
        this.profile = await Api.get("/api/student/profile");
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
    onFileChange(e) {
      this.resumeFile = e.target.files[0] || null;
    },
    async save() {
      this.error = ""; this.success = "";
      try {
        this.profile = await Api.put("/api/student/profile", {
          name: this.profile.name, department: this.profile.department,
          skills: this.profile.skills,
          cgpa: this.profile.cgpa, year: this.profile.year, phone: this.profile.phone,
        });
        this.success = "Profile updated.";
      } catch (e) {
        this.error = e.message;
      }
    },
    async uploadResume() {
      this.error = ""; this.success = "";
      const formData = new FormData();
      formData.append("resume", this.resumeFile);
      try {
        const res = await Api.postForm("/api/student/profile/resume", formData); //used cuz files are being sent along with text info
        this.profile.resume_filename = res.resume_filename;
        this.success = "Resume uploaded.";
      } catch (e) {
        this.error = e.message;
      }
    },
  },
};
