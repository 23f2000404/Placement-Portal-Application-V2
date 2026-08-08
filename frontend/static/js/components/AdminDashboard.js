const AdminDashboard = {
  data() {
    return {
      stats: {},
      companies: [],
      students: [],
      drives: [],
      applications: [],
      placements: [],
      searchQuery: "",
      searchResults: null,
      selectedCompany: null,
      selectedStudent: null,
      selectedDrive: null,
      error: "",
      loading: true,
    };   
  },

  async mounted() {
    await this.loadAll();
  },

  template: `
    <div class="container">
      <h3 class="mb-4">Welcome Admin</h3>
      <div class="alert alert-danger" v-if="error">{{ error }}</div>

      <!-- Stats -->
      <div class="row g-3 mb-4">
        <div class="col">
          <div class="stat-card">
            <small>Total Students</small>
            <h2>{{ stats.total_students ?? '-' }}</h2>
          </div>
        </div>

        <div class="col">
          <div class="stat-card">
            <small>Total Companies</small>
            <h2>{{ stats.total_companies ?? '-' }}</h2>
          </div>
        </div>

        <div class="col">
          <div class="stat-card">
            <small>Total Drives</small>
            <h2>{{ stats.total_drives ?? '-' }}</h2>
          </div>
        </div>

        <div class="col">
          <div class="stat-card">
            <small>Total Applications</small>
            <h2>{{ stats.total_applications ?? '-' }}</h2>
          </div>
        </div>

        <div class="col">
          <div class="stat-card">
            <small>Total Placed</small>
            <h2>{{ stats.total_placed ?? '-' }}</h2>
          </div>
        </div>
      </div>


      <!-- Search -->
      <div class="card card-pp p-3 mb-4">
        <form class="d-flex gap-2" @submit.prevent="search">
          <input v-model="searchQuery" class="form-control" placeholder="Search by name, industry, student ID, or contact.." />
          <button class="btn btn-pp">Search</button>
        </form>
        <div v-if="searchResults" class="mt-3">
          <div v-if="searchResults.companies.length">
            <b>Companies:</b> {{ searchResults.companies.map(c => c.company_name + (c.industry ? ' (' + c.industry + ')' : '')).join(', ') }}
          </div>
          <div v-if="searchResults.students.length">
            <b>Students:</b> {{ searchResults.students.map(s => s.name + ' #' + s.id).join(', ') }}
          </div>
          <div v-if="!searchResults.companies.length && !searchResults.students.length" class="text-muted">
            No matches found.
          </div>
        </div>
      </div>

      <div class="row g-4">

        <!-- Registered Companies -->
        <div class="col-lg-6">
          <div class="card card-pp p-3 h-100">
            <h5>Registered Companies</h5>
            <table class="table table-pp table-sm align-middle">
              <thead><tr><th>Name</th><th>Status</th><th></th></tr></thead>
              <tbody>
                <tr v-for="c in companies" :key="c.id" style="cursor: pointer;">
                  <td @click="viewCompanyDetail(c.id)">{{ c.company_name }}</td>
                  <td><span class="badge" :class="'badge-' + c.approval_status">{{ c.approval_status }}</span></td>
                  <td>
                    <button v-if="c.approval_status === 'pending'" class="btn btn-sm btn-pp me-1" @click="approveCompany(c)">Approve</button>
                    <button v-if="c.approval_status === 'pending'" class="btn btn-sm btn-outline-danger" @click="rejectCompany(c)">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Company Detail Modal -->
        <div class="modal fade" id="companyModal" tabindex="-1">
          <div class="modal-dialog modal-lg">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Company Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body" v-if="selectedCompany">
                <p><b>Name:</b> {{ selectedCompany.company_name }}</p>
                <p><b>Industry:</b> {{ selectedCompany.industry || '-' }}</p>
                <p><b>Location:</b> {{ selectedCompany.location || '-' }}</p>
                <p><b>Website:</b> {{ selectedCompany.website || '-' }}</p>
                <p><b>HR Contact:</b> {{ selectedCompany.hr_contact }} ({{ selectedCompany.hr_email }})</p>
                <p><b>Description:</b> {{ selectedCompany.description || '-' }}</p>
                <p><b>Status:</b> <span class="badge" :class="'badge-' + selectedCompany.approval_status">{{ selectedCompany.approval_status }}</span></p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button v-if="selectedCompany && selectedCompany.approval_status === 'pending'" type="button" class="btn btn-pp" @click="approveCompanyFromModal">Approve</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Registered Students -->
        <div class="col-lg-6">
          <div class="card card-pp p-3 h-100">
            <h5>Registered Students</h5>
            <table class="table table-pp table-sm align-middle">
              <thead><tr><th>Name</th><th>Dept</th><th></th></tr></thead>
              <tbody>
                <tr v-for="s in students" :key="s.id" style="cursor: pointer;">
                  <td @click="viewStudentDetail(s.id)">{{ s.name }}</td>
                  <td>{{ s.department }}</td>
                  <td>
                    <button class="btn btn-sm" :class="s.is_blacklisted ? 'btn-outline-secondary' : 'btn-outline-danger'"
                            @click="toggleBlacklistStudent(s)">
                      {{ s.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                    </button>
                  </td>
                </tr>
                <tr v-if="!students.length"><td colspan="3" class="text-muted">No students yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Student Detail Modal -->
        <div class="modal fade" id="studentModal" tabindex="-1">
          <div class="modal-dialog modal-lg">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Student Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body" v-if="selectedStudent">
                <p><b>Name:</b> {{ selectedStudent.name }}</p>
                <p><b>Department:</b> {{ selectedStudent.department || '-' }}</p>
                <p><b>CGPA:</b> {{ selectedStudent.cgpa }}</p>
                <p><b>Graduation Year:</b> {{ selectedStudent.year || '-' }}</p>
                <p><b>Skills:</b> {{ selectedStudent.skills || '-' }}</p>
                <p><b>Phone:</b> {{ selectedStudent.phone || '-' }}</p>
                <p><b>Resume:</b> <span v-if="selectedStudent.resume_filename" class="badge bg-success">{{ selectedStudent.resume_filename }}</span><span v-else class="text-muted">Not uploaded</span></p>
                <p><b>Status:</b> <span v-if="selectedStudent.is_blacklisted" class="badge bg-danger">Blacklisted</span><span v-else class="badge bg-success">Active</span></p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-outline-danger" @click="toggleBlacklistStudentFromModal">
                  {{ selectedStudent && selectedStudent.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Placement Drives -->
        <div class="col-lg-6">
          <div class="card card-pp p-3 h-100">
            <h5>Placement Drives</h5>
            <table class="table table-pp table-sm align-middle">
              <thead><tr><th>Job Title</th><th>Company</th><th>Status</th><th></th></tr></thead>
              <tbody>
                <tr v-for="d in drives" :key="d.id" style="cursor: pointer;">
                  <td @click="viewDriveDetail(d.id)">{{ d.job_title }}</td>
                  <td>{{ d.company_name }}</td>
                  <td><span class="badge" :class="'badge-' + d.status">{{ d.status }}</span></td>
                  <td>
                    <button v-if="d.status === 'pending'" class="btn btn-sm btn-pp me-1" @click="approveDrive(d)">Approve</button>
                    <button v-if="d.status === 'pending'" class="btn btn-sm btn-outline-danger" @click="rejectDrive(d)">Reject</button>
                  </td>
                </tr>
                <tr v-if="!drives.length"><td colspan="4" class="text-muted">No drives yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Drive Detail Modal -->
        <div class="modal fade" id="driveModal" tabindex="-1">
          <div class="modal-dialog modal-lg">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Placement Drive Details</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body" v-if="selectedDrive">
                <p><b>Job Title:</b> {{ selectedDrive.job_title }}</p>
                <p><b>Company:</b> {{ selectedDrive.company_name }}</p>
                <p><b>Job Description:</b> {{ selectedDrive.job_description || '-' }}</p>
                <p><b>Skills Required:</b> {{ selectedDrive.skills_required || '-' }}</p>
                <p><b>Experience Required:</b> {{ selectedDrive.experience_required || '-' }}</p>
                <p><b>Benefits:</b> {{ selectedDrive.benefits || '-' }}</p>
                <hr>
                <p><b>Salary:</b> ₹{{ selectedDrive.salary || 'N/A' }}</p>
                <p><b>Location:</b> {{ selectedDrive.location || '-' }}</p>
                <p><b>Application Deadline:</b> {{ selectedDrive.application_deadline }}</p>
                <hr>
                <p><b>Eligibility Criteria:</b></p>
                <ul class="small">
                  <li>Branch: {{ selectedDrive.eligibility_branch }}</li>
                  <li>Min CGPA: {{ selectedDrive.eligibility_cgpa }}</li>
                  <li>Graduation Year: {{ selectedDrive.eligibility_year || 'Any' }}</li>
                </ul>
                <p><b>Applications:</b> {{ selectedDrive.applicant_count }}</p>
                <p><b>Status:</b> <span class="badge" :class="'badge-' + selectedDrive.status">{{ selectedDrive.status }}</span></p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button v-if="selectedDrive && selectedDrive.status === 'pending'" type="button" class="btn btn-pp" @click="approveDriveFromModal">Approve</button>
                <button v-if="selectedDrive && selectedDrive.status === 'pending'" type="button" class="btn btn-outline-danger" @click="rejectDriveFromModal">Reject</button>
              </div>
            </div>
          </div>
        </div>
        <!-- Applications -->
        <div class="col-lg-6">
          <div class="card card-pp p-3 h-100">
            <h5>Student Applications</h5>
            <table class="table table-pp table-sm align-middle">
              <thead><tr><th>Name</th><th>Drive</th><th>Company</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="a in applications" :key="a.id">
                  <td>{{ a.student_name }}</td>
                  <td>{{ a.drive_title }}</td>
                  <td>{{ a.company_name }}</td>
                  <td><span class="badge" :class="'badge-' + a.status">{{ a.status }}</span></td>
                </tr>
                <tr v-if="!applications.length"><td colspan="4" class="text-muted">No applications yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Placements -->
        <div class="col-lg-6">
          <div class="card card-pp p-3 h-100">
            <h5>Placements</h5>
            <table class="table table-pp table-sm align-middle">
              <thead><tr><th>Student</th><th>Company</th><th>Position</th><th>Salary</th></tr></thead>
              <tbody>
                <tr v-for="p in placements" :key="p.id">
                  <td>{{ p.student_name }}</td>
                  <td>{{ p.company_name }}</td>
                  <td>{{ p.position }}</td>
                  <td>{{ p.salary || 'N/A' }}</td>
                </tr>
                <tr v-if="!placements.length"><td colspan="4" class="text-muted">No placements yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  `,

  methods: {
    async loadAll() {
      this.loading = true;
      try {
        const [stats, companies, students, drives, applications, placements] = await Promise.all([ //all these API calls can happen together
          Api.get("/api/admin/dashboard"),
          Api.get("/api/admin/companies"),
          Api.get("/api/admin/students"),
          Api.get("/api/admin/drives"),
          Api.get("/api/admin/applications"),
          Api.get("/api/admin/placements"),
        ]);
        this.stats = stats; 
        this.companies = companies; 
        this.students = students;
        this.drives = drives; 
        this.applications = applications; 
        this.placements = placements;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
//normal admin search
    async search() {
      const q = encodeURIComponent(this.searchQuery);
      const [companies, students] = await Promise.all([
        Api.get("/api/admin/search/companies?q=" + q),
        Api.get("/api/admin/search/students?q=" + q),
      ]);
      this.searchResults = { companies, students };
    },

    //viewing companies in details
    async viewCompanyDetail(companyId) {
      try {
        this.selectedCompany = await Api.get(`/api/admin/companies/${companyId}`);
        new bootstrap.Modal(document.getElementById('companyModal')).show();
      } catch (e) {
        this.error = e.message;
      }
    },
    async approveCompanyFromModal() {
      await this.approveCompany(this.selectedCompany);
      bootstrap.Modal.getInstance(document.getElementById('companyModal')).hide();
    },
//student details modal added
    async viewStudentDetail(studentId) {
      try {
        this.selectedStudent = await Api.get(`/api/admin/students/${studentId}`);
        new bootstrap.Modal(document.getElementById('studentModal')).show();
      } catch (e) {
        this.error = e.message;
      }
    },
    async toggleBlacklistStudentFromModal() {
      await this.toggleBlacklistStudent(this.selectedStudent);
      bootstrap.Modal.getInstance(document.getElementById('studentModal')).hide();
    },


    //drive details modal
    async viewDriveDetail(driveId) {
      try {
        this.selectedDrive = await Api.get(`/api/admin/drives/${driveId}`);
        new bootstrap.Modal(document.getElementById('driveModal')).show();
      } catch (e) {
        this.error = e.message;
      }
    },
    async approveDriveFromModal() {
      await this.approveDrive(this.selectedDrive);
      bootstrap.Modal.getInstance(document.getElementById('driveModal')).hide();
    },
    async rejectDriveFromModal() {
      await this.rejectDrive(this.selectedDrive);
      bootstrap.Modal.getInstance(document.getElementById('driveModal')).hide();
    },

    //simple async funcs for approvals, rejctions, toggles, etc
    async approveCompany(c) {
      await Api.post(`/api/admin/companies/${c.id}/approve`);
      this.loadAll();
    },

    async rejectCompany(c) {
      await Api.post(`/api/admin/companies/${c.id}/reject`);
      this.loadAll();
    },

    async toggleBlacklistCompany(c) {
      await Api.post(`/api/admin/companies/${c.id}/blacklist`);
      this.loadAll();
    },

    async toggleBlacklistStudent(s) {
      await Api.post(`/api/admin/students/${s.id}/blacklist`);
      this.loadAll();
    },

    async approveDrive(d) {
      await Api.post(`/api/admin/drives/${d.id}/approve`);
      this.loadAll();
    },

    async rejectDrive(d) {
      await Api.post(`/api/admin/drives/${d.id}/reject`);
      this.loadAll();
    },    
  },
};
