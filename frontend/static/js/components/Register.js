const Register = {
  emits: ["login-success"],
  data() {
    return {
      role: "student",
      username: "", password: "", email: "",
      name: "", department: "", skills: "", cgpa: "", year: "", phone: "",
      departments: DEPARTMENTS,
      company_name: "", industry: "", hr_contact: "", hr_email: "", website: "", location: "", description: "",
      error: "", success: "", loading: false,
    };
  },
  template: `
    <div class="auth-wrapper" style="max-width: 520px;">
      <div class="card card-pp p-4">
        <h3 class="mb-3 text-center">Register</h3>
        <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
        <div class="alert alert-success py-2" v-if="success">{{ success }}</div>

        <div class="btn-group w-100 mb-3">
          <button type="button" class="btn" :class="role==='student' ? 'btn-pp' : 'btn-outline-pp'" @click="role='student'">Student</button>
          <button type="button" class="btn" :class="role==='company' ? 'btn-pp' : 'btn-outline-pp'" @click="role='company'">Company</button>
        </div>

        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model="username" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required />
          </div>

          <template v-if="role === 'student'">
            <div class="mb-3"><label class="form-label">Full Name</label>
              <input v-model="name" class="form-control" required /></div>
            <div class="row">
              <div class="col mb-3"><label class="form-label">Department</label>
                <select v-model="department" class="form-control" required>
                  <option value="" disabled>Select department</option>
                  <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
                </select></div>
              <div class="col mb-3"><label class="form-label">CGPA</label>
                <input v-model="cgpa" type="number" step="0.01" class="form-control" required/></div>
            </div>
            <div class="row">
              <div class="col mb-3"><label class="form-label">Graduation Year</label>
                <input v-model="year" type="number" class="form-control" required/></div>
              <div class="col mb-3"><label class="form-label">Phone</label>
                <input  v-model="phone"  type="tel"  class="form-control" pattern="[0-9]{10}" maxlength="10" minlength="10" required/></div>
            </div>
            <div class="mb-3"><label class="form-label">Skills</label>
              <input v-model="skills" class="form-control" placeholder="e.g. Python, React, SQL" /></div>
          </template>

          <template v-else>
            <div class="mb-3"><label class="form-label">Company Name</label>
              <input v-model="company_name" class="form-control" required /></div>
            <div class="row">
              <div class="col mb-3"><label class="form-label">Industry</label>
                <input v-model="industry" class="form-control" placeholder="e.g. IT Services" required/></div>
              <div class="col mb-3"><label class="form-label">Location</label>
                <input v-model="location" class="form-control" required/></div>
            </div>
            <div class="row">
              <div class="col mb-3"><label class="form-label">HR Contact</label>
                <input v-model="hr_contact" class="form-control" required/></div>
              <div class="col mb-3"><label class="form-label">HR Email</label>
                <input v-model="hr_email" type="email" class="form-control" placeholder="For monthly reports (eg: name@domain.com)" required/></div>
            </div>
            <div class="mb-3"><label class="form-label">Website</label>
              <input v-model="website" class="form-control" placeholder="https://" /></div>
            <div class="mb-3"><label class="form-label">Description</label>
              <textarea v-model="description" class="form-control" rows="2"></textarea></div>
          </template>

          <button class="btn btn-pp w-100" :disabled="loading">
            {{ loading ? 'Registering...' : 'Register' }}
          </button>
        </form>
        <p class="text-center mt-3 mb-0">
          Already have an account? <router-link to="/login">Login</router-link>
        </p>
      </div>
    </div>
  `,
  methods: {
    async submit() {
      this.error = ""; this.success = "";
      this.loading = true;  //payload means the data user is sending in the request body to da Api
      const payload = {
        role: this.role, username: this.username, password: this.password, email: this.email,
      };

      if (this.role === "student") {
        Object.assign(payload, { name: this.name, department: this.department, skills: this.skills,
          cgpa: this.cgpa, year: this.year, phone: this.phone,
        });
      } else {
        Object.assign(payload, { company_name: this.company_name, industry: this.industry,
          hr_contact: this.hr_contact, hr_email: this.hr_email,
          website: this.website, location: this.location, description: this.description,
        });
      }
      try {
        await Api.post("/api/auth/register", payload);
        // auto-login after registration
        const data = await Api.post("/api/auth/login", {
          username: this.username, password: this.password,
        });
        this.$emit("login-success", data.user);
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  },
};