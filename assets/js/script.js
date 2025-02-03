// تحميل الشهادات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    let allCertificates = []; // المصفوفة الأصلية
    let displayedCertificates = []; // المصفوفة المفلترة
    let currentCertificateIndex = 0;
    let years = new Set();
    
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const yearFilter = document.getElementById('yearFilter');
    const certificatesCount = document.getElementById('certificatesCount');
    const certificateTemplate = document.getElementById('certificateTemplate').innerHTML;
    const certificateModal = new bootstrap.Modal(document.getElementById('certificateModal'));

    // تحميل البيانات
    fetch('/api/certificates')
        .then(response => response.json())
        .then(data => {
            // تنقية البيانات وإضافة معرف فريد
            allCertificates = data
                .filter(cert => cert.certificate_url && cert.certificate_url.trim() !== '')
                .map((cert, index) => ({
                    ...cert,
                    id: index, // إضافة معرف ثابت
                    employeeName: cert.employee_name || 'غير محدد',
                    department: cert.department || 'غير محدد',
                    designation: cert.designation || 'غير محدد',
                    certificateName: cert.employee_courses_degree.certificate_name || 'غير محدد',
                    certificateDate: cert.employee_courses_degree.certificate_date,
                    certificateUrl: cert.certificate_url
                }));
            
            // استخراج السنوات
            allCertificates.forEach(cert => {
                if (cert.certificateDate) {
                    const year = new Date(cert.certificateDate).getFullYear();
                    if (!isNaN(year)) {
                        years.add(year);
                    }
                }
            });

            displayedCertificates = [...allCertificates];
            updateFilters(allCertificates);
            displayCertificates(displayedCertificates);
        })
        .catch(error => console.error('Error:', error));

    // تحديث قائمة الإدارات
    function updateFilters(certificates) {
        const departments = new Set();
        certificates.forEach(cert => {
            if (cert.department && cert.department !== 'غير محدد') {
                departments.add(cert.department);
            }
        });

        const sortedDepartments = Array.from(departments).sort((a, b) => 
            a.localeCompare(b, 'ar')
        );

        departmentFilter.innerHTML = '<option value="">كل الإدارات</option>';
        sortedDepartments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            option.textContent = dept;
            departmentFilter.appendChild(option);
        });

        // ملء قائمة السنوات
        yearFilter.innerHTML = '<option value="">كل السنوات</option>';
        [...years].sort((a, b) => b - a).forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearFilter.appendChild(option);
        });
    }

    // تحديث عداد الشهادات
    function updateCertificatesCount(count) {
        certificatesCount.textContent = count;
        const label = document.querySelector('.counter-label');
        if (count === 1) {
            label.textContent = 'شهادة مهنية';
        } else if (count === 2) {
            label.textContent = 'شهادتان مهنيتان';
        } else if (count >= 3 && count <= 10) {
            label.textContent = 'شهادات مهنية';
        } else {
            label.textContent = 'شهادة مهنية';
        }
    }

    // عرض الشهادات
    function displayCertificates(certificates) {
        const container = document.getElementById('certificatesContainer');
        container.innerHTML = '';
        displayedCertificates = [...certificates];

        if (certificates.length === 0) {
            container.innerHTML = '<div class="col-12 text-center mt-5"><p class="text-muted">لا توجد شهادات متاحة</p></div>';
            updateCertificatesCount(0);
            return;
        }

        certificates.forEach(cert => {
            const cardHtml = `
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card h-100 certificate-card">
                        <div class="certificate-image-container">
                            <img src="${cert.certificateUrl}" 
                                 class="card-img-top certificate-image" 
                                 alt="شهادة ${cert.employeeName}"
                                 data-certificate-id="${cert.id}">
                        </div>
                        <div class="card-body text-center">
                            <h5 class="card-title mb-3">${cert.employeeName}</h5>
                            <p class="card-text mb-2">
                                <i class="fas fa-building ml-2"></i>
                                ${cert.department}
                            </p>
                            <p class="card-text mb-2">
                                <i class="fas fa-user-tie ml-2"></i>
                                ${cert.designation}
                            </p>
                            <p class="card-text mb-2">
                                <i class="fas fa-certificate ml-2"></i>
                                ${cert.certificateName}
                            </p>
                            <p class="card-text">
                                <i class="fas fa-calendar-alt ml-2"></i>
                                ${formatDate(cert.certificateDate)}
                            </p>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', cardHtml);
        });

        updateCertificatesCount(certificates.length);

        // إضافة معالج النقر على الصور
        document.querySelectorAll('.certificate-image').forEach(img => {
            img.addEventListener('click', function() {
                const certId = parseInt(this.getAttribute('data-certificate-id'));
                const certIndex = displayedCertificates.findIndex(cert => cert.id === certId);
                if (certIndex !== -1) {
                    showCertificateModal(certIndex);
                }
            });
        });
    }

    // عرض النافذة المنبثقة
    function showCertificateModal(index) {
        if (index < 0 || index >= displayedCertificates.length) {
            console.error('Invalid certificate index:', index);
            return;
        }

        currentCertificateIndex = index;
        const cert = displayedCertificates[index];

        if (!cert) {
            console.error('Certificate not found at index:', index);
            return;
        }

        document.getElementById('modalCertificateImage').src = cert.certificateUrl;
        document.getElementById('modalEmployeeName').textContent = cert.employeeName;
        document.getElementById('modalDepartment').textContent = cert.department;
        document.getElementById('modalDesignation').textContent = cert.designation;
        document.getElementById('modalCertificateName').textContent = cert.certificateName;
        document.getElementById('modalCertificateDate').textContent = formatDate(cert.certificateDate);

        certificateModal.show();
    }

    // التنقل بين الشهادات
    document.getElementById('prevCertificate').addEventListener('click', function() {
        currentCertificateIndex = (currentCertificateIndex - 1 + displayedCertificates.length) % displayedCertificates.length;
        showCertificateModal(currentCertificateIndex);
    });

    document.getElementById('nextCertificate').addEventListener('click', function() {
        currentCertificateIndex = (currentCertificateIndex + 1) % displayedCertificates.length;
        showCertificateModal(currentCertificateIndex);
    });

    // تنسيق التاريخ
    function formatDate(dateString) {
        if (!dateString || dateString === 'NaT') return 'غير محدد';
        try {
            const date = new Date(dateString);
            return new Intl.DateTimeFormat('ar-SA', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(date);
        } catch {
            return 'غير محدد';
        }
    }

    // البحث والفلترة
    function filterCertificates() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedDepartment = departmentFilter.value;
        const selectedYear = yearFilter.value;

        const filtered = allCertificates.filter(cert => {
            const matchesSearch = 
                (cert.employeeName.toLowerCase().includes(searchTerm) || 
                cert.certificateName.toLowerCase().includes(searchTerm));

            const matchesDepartment = !selectedDepartment || cert.department === selectedDepartment;

            let certYear = null;
            if (cert.certificateDate) {
                certYear = new Date(cert.certificateDate).getFullYear().toString();
            }
            const matchesYear = !selectedYear || certYear === selectedYear;

            return matchesSearch && matchesDepartment && matchesYear;
        });

        displayCertificates(filtered);
    }

    // إضافة مستمعي الأحداث
    searchInput.addEventListener('input', filterCertificates);
    departmentFilter.addEventListener('change', filterCertificates);
    yearFilter.addEventListener('change', filterCertificates);

    // إضافة دعم لوحة المفاتيح للتنقل
    document.addEventListener('keydown', function(e) {
        if (document.getElementById('certificateModal').classList.contains('show')) {
            if (e.key === 'ArrowRight') {
                document.getElementById('prevCertificate').click();
            } else if (e.key === 'ArrowLeft') {
                document.getElementById('nextCertificate').click();
            } else if (e.key === 'Escape') {
                certificateModal.hide();
            }
        }
    });
});
