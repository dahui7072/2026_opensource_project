// 차트 인스턴스 전역 관리 (중복 생성 에러 및 튕김 방지)
let hourlyChartInstance = null;
let ratioChartInstance = null;

async function updateDashboard() {
    try {
        // 백엔드 CSV 변환 API 호출
        const res = await fetch('/data');
        const json = await res.json();

        const data = json.violations;
        const avgConf = json.avg_confidence;

        // 1. 위반 카운팅 변수 초기화
        let totalCount = data.length;
        let helmetCount = 0;
        let twoPersonCount = 0;

        // 시간대별 카운트 배열 생성 (0시 ~ 23시)
        const hourlyCounts = Array(24).fill(0);

        // 데이터 가공 및 카운트
        data.forEach(item => {
            // 위반 유형 매핑 데이터 카운트
            if (item.violation_type === 'no_helmet') helmetCount++;
            if (item.violation_type === 'two_person') twoPersonCount++;

            // 시간대별 위반 건수 계산 추출 (포맷: "2026-05-23 14:32:11")
            if (item.timestamp) {
                const timePart = item.timestamp.split(' ')[1]; // "14:32:11" 추출
                if (timePart) {
                    const hour = parseInt(timePart.split(':')[0], 10); // 14 추출
                    if (!isNaN(hour) && hour >= 0 && hour < 24) {
                        hourlyCounts[hour]++;
                    }
                }
            }
        });

        // 2. 우측 상단 KPI 카드에 숫자 실시간 매핑 변경
        document.getElementById('statTotalCount').innerText = totalCount;
        document.getElementById('statHelmetCount').innerText = helmetCount;
        document.getElementById('statTwoPersonCount').innerText = twoPersonCount;
        document.getElementById('statAccuracy').innerText = avgConf + "%";

        // 3. 실시간 테이블 로`그 출력 가공 (최신 로그 30개 제한 출력)
        const tableBody = document.getElementById('logTableBody');
        if (tableBody) {
            tableBody.innerHTML = '';
            
            // 최근 기록이 위로 가도록 역순 배치
            const recentLogs = [...data].reverse().slice(0, 30);

            recentLogs.forEach(item => {
                const row = document.createElement('tr');
                
                // 요구사항 반영한 한글 텍스트 매핑 변환 로직
                let koreanType = "정상";
                let colorStyle = "#e2e8f0";
                
                if (item.violation_type === 'no_helmet') {
                    koreanType = "🚨 헬멧 미착용";
                    colorStyle = "#ef4444"; // 빨간색
                } else if (item.violation_type === 'two_person') {
                    koreanType = "❌ 2인 탑승";
                    colorStyle = "#f59e0b"; // 주황색
                }

                row.innerHTML = `
                    <td style="color: #94a3b8; font-family: monospace;">${item.timestamp}</td>
                    <td style="color: ${colorStyle}; font-weight: bold;">${koreanType}</td>
                `;
                tableBody.appendChild(row);
            });
        }

        // 4. 하단 차트 가동 시각화 (Chart.js 연동)
        const ctxHourly = document.getElementById('hourlyChart').getContext('2d');
        const ctxRatio = document.getElementById('ratioChart').getContext('2d');

        // [차트 1] 시간대별 위반 건수 (막대 차트)
        if (hourlyChartInstance) hourlyChartInstance.destroy(); // 초기화 재실행 방지
        hourlyChartInstance = new Chart(ctxHourly, {
            type: 'bar',
            data: {
                labels: Array.from({length: 24}, (_, i) => `${i}시`),
                datasets: [{
                    label: '위반 건수',
                    data: hourlyCounts,
                    backgroundColor: '#38bdf8',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
                    y: { beginAtZero: true, grid: { color: '#1f293d' }, ticks: { color: '#94a3b8', stepSize: 1 } }
                }
            }
        });

        // [차트 2] 위반 유형 비율 (도넛 차트)
        if (ratioChartInstance) ratioChartInstance.destroy();
        ratioChartInstance = new Chart(ctxRatio, {
            type: 'doughnut',
            data: {
                labels: ['헬멧 미착용', '2인 탑승'],
                datasets: [{
                    data: [helmetCount, twoPersonCount],
                    backgroundColor: ['#ef4444', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', boxWidth: 12, font: { size: 11 } }
                    }
                },
                cutout: '70%'
            }
        });

    } catch (error) {
        console.error("CSV 데이터를 읽어오지 못했습니다:", error);
    }
}

// 최초 1회 실행 후 5초 간격 실시간 자동 비동기 업데이트 갱신
updateDashboard();
setInterval(updateDashboard, 5000);