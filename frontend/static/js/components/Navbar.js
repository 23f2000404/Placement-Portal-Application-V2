const Navbar = {
  props: ["user"],
  emits: ["logout"],
  template: `
    <nav class="navbar navbar-expand-lg navbar-pp mb-4 shadow-sm">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="bi bi-mortarboard-fill me-1"></i> Placement Portal
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navContent">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navContent">
          <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-2">
            <template v-if="user && user.role === 'admin'">
              <li class="nav-item"><router-link class="nav-link" to="/admin">Dashboard</router-link></li>
            </template>
            <template v-else-if="user && user.role === 'company'">
              <li class="nav-item"><router-link class="nav-link" to="/company">Dashboard</router-link></li>
            </template>
            <template v-else-if="user && user.role === 'student'">
              <li class="nav-item"><router-link class="nav-link" to="/student">Drives</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/student/profile">Profile</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/student/history">History</router-link></li>
            </template>
            <li class="nav-item" v-if="user">
              <span class="nav-link"><i class="bi bi-person-circle me-1"></i>{{ user.username }}</span>
            </li>
            <li class="nav-item" v-if="user">
              <button class="btn btn-sm btn-outline-light" @click="$emit('logout')">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  `,
};
