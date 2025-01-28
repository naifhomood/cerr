// Load certificates when the page loads
document.addEventListener('DOMContentLoaded', function() {
    let certificates = [];
    let currentCertificateIndex = 0;
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const certificatesCount = document.getElementById('certificatesCount');
    const certificateTemplate = document.getElementById('certificateTemplate').innerHTML;
    const certificateModal = new bootstrap.Modal(document.getElementById('certificateModal'));
    
    // تحميل البيانات
    fetch('/api/certificates')
        .then(response => response.json())
        .then(data => {
            certificates = data.filter(cert => cert['certificate url'] && cert['certificate url'].trim() !== '');
            updateFilters(certificates);
            displayCertificates(certificates);
        })
        .catch(error => console.error('Error:', error));

    // تحديث قائمة الإدارات
    function updateFilters(certificates) {
        const departments = new Set();
        certificates.forEach(cert => {
            if (cert['Column1.department']) {
                departments.add(cert['Column1.department']);
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
    }

    // تحديث عداد الشهادات
    function updateCertificatesCount(count) {
        certificatesCount.textContent = count;
        
        // تحديث نص "شهادة" حسب العدد
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

        if (certificates.length === 0) {
            container.innerHTML = '<div class="col-12 text-center mt-5"><p class="text-muted">لا توجد شهادات متاحة</p></div>';
            updateCertificatesCount(0);
            return;
        }

        certificates.forEach((cert, index) => {
            if (cert['certificate url'] && cert['certificate url'].trim() !== '') {
                let cardHtml = certificateTemplate
                    .replace('%employee_name%', cert['Column1.employee_name'] || 'غير محدد')
                    .replace('%department%', cert['Column1.department'] || 'غير محدد')
                    .replace('%designation%', cert['Column1.designation'] || 'غير محدد')
                    .replace('%certificate_name%', cert['Column1.employee_courses_degree.certificate_name'] || 'غير محدد')
                    .replace('%certificate_date%', formatDate(cert['Column1.employee_courses_degree.certificate_date']))
                    .replace('%certificate_image%', cert['certificate url'])
                    .replace('%index%', index);

                container.innerHTML += cardHtml;
            }
        });

        // تحديث العداد
        updateCertificatesCount(certificates.length);

        // إضافة معالج النقر على الصور
        document.querySelectorAll('.certificate-image').forEach(img => {
            img.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-certificate-id'));
                showCertificateModal(index);
            });
        });
    }

    // عرض النافذة المنبثقة
    function showCertificateModal(index) {
        currentCertificateIndex = index;
        const cert = certificates[index];
        
        document.getElementById('modalCertificateImage').src = cert['certificate url'];
        document.getElementById('modalEmployeeName').textContent = cert['Column1.employee_name'] || 'غير محدد';
        document.getElementById('modalDepartment').textContent = cert['Column1.department'] || 'غير محدد';
        document.getElementById('modalDesignation').textContent = cert['Column1.designation'] || 'غير محدد';
        document.getElementById('modalCertificateName').textContent = cert['Column1.employee_courses_degree.certificate_name'] || 'غير محدد';
        document.getElementById('modalCertificateDate').textContent = formatDate(cert['Column1.employee_courses_degree.certificate_date']);

        certificateModal.show();
    }

    // التنقل بين الشهادات
    document.getElementById('prevCertificate').addEventListener('click', function() {
        currentCertificateIndex = (currentCertificateIndex - 1 + certificates.length) % certificates.length;
        showCertificateModal(currentCertificateIndex);
    });

    document.getElementById('nextCertificate').addEventListener('click', function() {
        currentCertificateIndex = (currentCertificateIndex + 1) % certificates.length;
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

        const filtered = certificates.filter(cert => {
            const matchesSearch = 
                (cert['Column1.employee_name']?.toLowerCase().includes(searchTerm) || 
                cert['Column1.employee_courses_degree.certificate_name']?.toLowerCase().includes(searchTerm));

            const matchesDepartment = !selectedDepartment || cert['Column1.department'] === selectedDepartment;

            return matchesSearch && matchesDepartment && cert['certificate url'] && cert['certificate url'].trim() !== '';
        });

        displayCertificates(filtered);
    }

    // إضافة مستمعي الأحداث
    searchInput.addEventListener('input', filterCertificates);
    departmentFilter.addEventListener('change', filterCertificates);

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
