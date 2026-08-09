const RootApp = {
  components: { Navbar },
  data() {
    return { user: null, ready: false };
  },
  async created() {
    try {
      const data = await Api.get("/api/auth/me");
      this.user = data.user;
    } catch (e) {
      this.user = null;
    } finally {
      window.__ppCurrentUser = this.user;
      this.ready = true;
      // re-run the guard now that we know the auth state
      router.replace(router.currentRoute.value.fullPath);
      window.authCheckInitialized = true;
    }
  },
  template: `
    <div v-if="ready">
      <navbar :user="user" @logout="logout"></navbar>
      <router-view @login-success="onLoginSuccess"></router-view>
    </div>
    <div v-else class="d-flex justify-content-center align-items-center" style="height: 100vh;">
      <div class="spinner-border" style="color:#7c3aed;" role="status"></div>
    </div>
  `,
  methods: {
    onLoginSuccess(user) {
      this.user = user;
      window.__ppCurrentUser = user;
      this.$router.push(`/${user.role}`);
    },
    async logout() {
      await Api.post("/api/auth/logout");
      this.user = null;
      window.__ppCurrentUser = null;
      this.$router.push("/login");
    },
  },
};

const app = Vue.createApp(RootApp);
app.use(router);

app.mount("#app");
