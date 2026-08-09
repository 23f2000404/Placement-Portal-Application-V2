const Login = {
  emits: ["login-success"],
  data() {
    return { username: "", password: "", error: "", loading: false };
  },
  template: `
    <div class="auth-wrapper">
      <div class="card card-pp p-4">
        <h3 class="mb-3 text-center">Login</h3>
        <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model="username" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required />
          </div>
          <button class="btn btn-pp w-100" :disabled="loading">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        <p class="text-center mt-3 mb-0">
          Do not have an account? <router-link to="/register">Register</router-link>
        </p>

      </div>
    </div>
  `,
  methods: {
    async submit() {
      this.error = "";
      this.loading = true;
      try {
        const data = await Api.post("/api/auth/login", {
          username: this.username,
          password: this.password,
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
