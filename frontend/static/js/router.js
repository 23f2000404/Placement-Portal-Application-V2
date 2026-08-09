const routes = [
  { path: "/login", name: "login", component: Login, meta: { public: true } },
  { path: "/register", name: "register", component: Register, meta: { public: true } },

  { path: "/admin", name: "admin", component: AdminDashboard, meta: { roles: ["admin"] } },

  { path: "/company", name: "company", component: CompanyDashboard, meta: { roles: ["company"] } },
  { path: "/company/create-drive", name: "create-drive", component: CreateDrive, meta: { roles: ["company"] } },
  { path: "/company/drives/:id/applications", name: "drive-applications", component: DriveApplications, meta: { roles: ["company"] } },

  { path: "/student", name: "student", component: StudentDashboard, meta: { roles: ["student"] } },
  { path: "/student/drives/:id", name: "drive-detail", component: DriveDetail, meta: { roles: ["student"] } },
  { path: "/student/profile", name: "student-profile", component: StudentProfile, meta: { roles: ["student"] } },
  { path: "/student/history", name: "student-history", component: StudentHistory, meta: { roles: ["student"] } },

  // fallback - redirect handled in app.js based on auth state
  { path: "/", name: "home", redirect: "/login" },
  { path: "/:pathMatch(.*)*", redirect: "/login" },
];

const router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const user = window.__ppCurrentUser;

  // Imma skip guard during initial app load while auth check ist still pending
  if (window.authCheckInitialized === undefined) {
    console.log("Auth check pending, allowing initial navigation");
    return true;
  }

  //Normal guard logic afterwards
  if (!to.meta.public && !user) {
    return "/login";
  }
  if (to.meta.public && user) {
    return `/${user.role}`;
  }
  if (to.meta.roles && user && !to.meta.roles.includes(user.role)) {
    return `/${user.role}`;
  }
  return true;
});