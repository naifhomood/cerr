// تحميل الشهادات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    let allCertificates = []; // المصفوفة الأصلية
    let displayedCertificates = []; // المصفوفة المفلترة
    let currentCertificateIndex = 0;
    let years = new Set();
    let lastModified = ''; // لتتبع آخر تحديث للملف
    
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const yearFilter = document.getElementById('yearFilter');
    const certificatesCount = document.getElementById('certificatesCount');
    const certificateTemplate = document.getElementById('certificateTemplate').innerHTML;
    const certificateModal = new bootstrap.Modal(document.getElementById('certificateModal'));
    const certificatesContainer = document.getElementById('certificatesContainer');

    // إضافة زر التحديث في أعلى الصفحة
    const filterRow = document.querySelector('.row.mb-4');
    const refreshButton = document.createElement('div');
    refreshButton.className = 'col-md-2';
    refreshButton.innerHTML = `
        <button class="btn btn-primary w-100" onclick="window.location.reload()">
            <i class="fas fa-sync-alt"></i>
            تحديث البيانات
        </button>
    `;
    filterRow.insertBefore(refreshButton, filterRow.firstChild);

    // دالة تحديث البيانات
    async function updateData() {
        try {
            // التحقق من تاريخ آخر تعديل للملف
            const response = await fetch('data/certificates.xlsx', { method: 'HEAD' });
            const currentModified = response.headers.get('last-modified');
            
            // إذا لم يتغير الملف، لا داعي للتحديث
            if (currentModified === lastModified) {
                return;
            }
            
            lastModified = currentModified;
            
            // تحميل البيانات من ملف Excel
            fetch('data/certificates.xlsx')
                .then(response => response.arrayBuffer())
                .then(buffer => {
                    const workbook = XLSX.read(buffer, { type: 'array' });
                    const worksheet = workbook.Sheets[workbook.SheetNames[0]];
                    const data = XLSX.utils.sheet_to_json(worksheet);
                    
                    if (data.length > 0) {
                        console.log('أسماء الأعمدة في ملف Excel:', Object.keys(data[0]));
                        console.log('نموذج للبيانات:', data[0]);
                    }

                    console.log('Excel Data:', data); // للتحقق من البيانات

                    // تنقية البيانات وإضافة معرف فريد
                    allCertificates = data.map((cert, index) => ({
                        id: index,
                        'Column1.name': cert['Column1.name'] || 'غير محدد',
                        'Column1.department': cert['Column1.department'] || 'غير محدد',
                        'Column1.employee_name': cert['Column1.employee_name'] || cert['Column1.name'] || 'غير محدد',
                        'Column1.designation': cert['Column1.designation'] || 'غير محدد',
                        'Column1.date_of_joining': cert['Column1.date_of_joining'] || 'غير محدد',
                        'Column1.branch': cert['Column1.branch'] || 'غير محدد',
                        'Column1.gender': cert['Column1.gender'] || 'غير محدد',
                        'urlnext': cert['urlnext'] || ''
                    }));

                    console.log('Mapped Certificates:', allCertificates); // للتحقق من البيانات بعد التحويل

                    // فلترة السجلات التي تحتوي على شهادات (تم إزالة الفلترة مؤقتاً للتحقق من البيانات)
                    displayedCertificates = [...allCertificates];
                    
                    console.log('Final Certificates:', displayedCertificates); // للتحقق من البيانات النهائية

                    // استخراج السنوات
                    displayedCertificates.forEach(cert => {
                        if (cert['Column1.date_of_joining'] && cert['Column1.date_of_joining'] !== 'غير محدد') {
                            const year = new Date(cert['Column1.date_of_joining']).getFullYear();
                            if (!isNaN(year)) {
                                years.add(year);
                            }
                        }
                    });

                    updateFilters(allCertificates);
                    displayCertificates(displayedCertificates);
                })
                .catch(error => {
                    console.error('Error loading Excel file:', error);
                    alert('حدث خطأ أثناء تحميل البيانات. يرجى التحقق من وجود ملف Excel في المجلد الصحيح.');
                });
        } catch (error) {
            console.error('Error:', error);
            showUpdateMessage('حدث خطأ أثناء تحديث البيانات', true);
        }
    }

    // دالة عرض الشهادات
    function displayCertificates(certificates) {
        certificatesContainer.innerHTML = '';
        certificates.forEach((cert, index) => {
            let cardHtml = certificateTemplate
                .replace(/%certificate_image%/g, cert.urlnext || 'assets/images/default-certificate.jpg')
                .replace(/%index%/g, index)
                .replace(/%employee_name%/g, cert['Column1.name'] || cert['Column1.employee_name'] || 'غير محدد')
                .replace(/%department%/g, cert['Column1.department'] || 'غير محدد')
                .replace(/%designation%/g, cert['Column1.designation'] || 'غير محدد')
                .replace(/%certificate_name%/g, cert['Column1.name'] || 'غير محدد')
                .replace(/%certificate_date%/g, formatDate(cert['Column1.date_of_joining'] || 'غير محدد'));

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = cardHtml;
            certificatesContainer.appendChild(tempDiv.firstElementChild);
        });

        // تحديث عداد الشهادات
        certificatesCount.textContent = certificates.length;
    }

    // دالة إظهار رسالة التحديث
    function showUpdateMessage(message, isError = false) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${isError ? 'danger' : 'success'} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '1050';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // إخفاء الرسالة بعد 3 ثواني
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }

    // تحديث البيانات كل دقيقة
    setInterval(updateData, 60000);
    
    // التحديث الأولي للبيانات
    updateData();

    // تحديث قائمة الإدارات
    function updateFilters(certificates) {
        const departments = new Set();
        certificates.forEach(cert => {
            if (cert['Column1.department'] && cert['Column1.department'] !== 'غير محدد') {
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
                            <img src="${cert.urlnext}" 
                                 class="card-img-top certificate-image" 
                                 alt="شهادة ${cert['Column1.name']}"
                                 data-certificate-id="${cert.id}">
                        </div>
                        <div class="card-body text-center">
                            <h5 class="card-title mb-3">${cert['Column1.name']}</h5>
                            <p class="card-text mb-2">
                                <i class="fas fa-building ml-2"></i>
                                ${cert['Column1.department']}
                            </p>
                            <p class="card-text mb-2">
                                <i class="fas fa-user-tie ml-2"></i>
                                ${cert['Column1.designation']}
                            </p>
                            <p class="card-text mb-2">
                                <i class="fas fa-certificate ml-2"></i>
                                ${cert['Column1.name']}
                            </p>
                            <p class="card-text">
                                <i class="fas fa-calendar-alt ml-2"></i>
                                ${formatDate(cert['Column1.date_of_joining'])}
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

        document.getElementById('modalCertificateImage').src = cert.urlnext;
        document.getElementById('modalEmployeeName').textContent = cert['Column1.name'];
        document.getElementById('modalDepartment').textContent = cert['Column1.department'];
        document.getElementById('modalDesignation').textContent = cert['Column1.designation'];
        document.getElementById('modalCertificateName').textContent = cert['Column1.name'];
        document.getElementById('modalCertificateDate').textContent = formatDate(cert['Column1.date_of_joining']);

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
                (cert['Column1.name'].toLowerCase().includes(searchTerm) || 
                cert['Column1.name'].toLowerCase().includes(searchTerm));

            const matchesDepartment = !selectedDepartment || cert['Column1.department'] === selectedDepartment;

            let certYear = null;
            if (cert['Column1.date_of_joining']) {
                certYear = new Date(cert['Column1.date_of_joining']).getFullYear().toString();
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
