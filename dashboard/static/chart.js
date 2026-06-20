let hourlyChartInstance = null;
let ratioChartInstance = null;

async function updateDashboard() {
    try {
        const res = await fetch('/data');
        const json = await res.json();

        const data = json.violations;
        const avgConf = json.avg_confidence;

        let totalCount = data.length;
        let helmetCount = 0;
        let twoPersonCount = 0;

        const hourlyCounts = Array(24).fill(0);

        data.forEach(item => {
            if (item.violation_type === 'no_helmet') helmetCount++;
            if (item.violation_type === 'two_person') twoPersonCount++;

            if (item.timestamp) {
                const timePart = item.timestamp.split(' ')[1];
                if (timePart) {
                    const hour = parseInt(timePart.split(':')[0], 10);
                    if (!isNaN(hour) && hour >= 0 && hour < 24) {
                        hourlyCounts[hour]++;
                    }
                }
            }
        });

        document.getElementById('statTotalCount').innerText = totalCount;
        document.getElementById('statHelmetCount').innerText = helmetCount;
        document.getElementById('statTwoPersonCount').innerText = twoPersonCount;
        document.getElementById('statAccuracy').innerText = avgConf + "%";

        const tableBody = document.getElementById('logTableBody');
        if (tableBody) {
            tableBody.innerHTML = '';
            const recentLogs = [...data].reverse().slice(0, 30);

            recentLogs.forEach(item => {
                const row = document.createElement('tr');
                let koreanType = "정상";
                let colorStyle = "#e2e8f0";

                if (item.violation_type === 'no_helmet') {
                    koreanType = "🚨 헬멧 미착용";
                    colorStyle = "#ef4444";
                } else if (item.violation_type === 'two_person') {
                    koreanType = "❌ 2인 탑승";
                    colorStyle = "#f59e0b";
                }

                row.innerHTML = `
                    <td style="color: #94a3b8; font-family: monospace;">${item.timestamp}</td>
                    <td style="color: ${colorStyle}; font-weight: bold;">${koreanType}</td>
                `;
                tableBody.appendChild(row);
            });
        }

        const ctxHourly = document.getElementById('hourlyChart').getContext('2d');
        const ctxRatio = document.getElementById('ratioChart').getContext('2d');

        // [차트 1] 시간대별 위반 건수 — 있으면 데이터만 갱신, 없으면 새로 생성
        if (hourlyChartInstance) {
            hourlyChartInstance.data.datasets[0].data = hourlyCounts;
            hourlyChartInstance.update();
        } else {
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
        }

        // [차트 2] 위반 유형 비율 — 있으면 데이터만 갱신, 없으면 새로 생성
        if (ratioChartInstance) {
            ratioChartInstance.data.datasets[0].data = [helmetCount, twoPersonCount];
            ratioChartInstance.update();
        } else {
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
        }

    } catch (error) {
        console.error("CSV 데이터를 읽어오지 못했습니다:", error);
    }
}

updateDashboard();
setInterval(updateDashboard, 5000);