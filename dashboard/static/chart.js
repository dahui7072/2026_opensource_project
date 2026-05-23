async function loadChart() {
    const res = await fetch('/data');
    const data = await res.json();

    let twoPersonCount = 0;
    let noHelmetCount = 0;

    data.forEach(d => {
        if (d.violation_type === 'two_person') twoPersonCount++;
        if (d.violation_type === 'no_helmet') noHelmetCount++;
    });

    const ctx = document.getElementById('violationChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['2인 탑승', '헬멧 미착용'],
            datasets: [{
                label: '위반 건수',
                data: [twoPersonCount, noHelmetCount],
                backgroundColor: ['#ff4444', '#ff8800']
            }]
        }
    });
}

loadChart();
setInterval(loadChart, 5000);  // 5초마다 갱신