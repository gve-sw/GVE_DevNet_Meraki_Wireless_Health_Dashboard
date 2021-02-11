$('#loader').hide();

var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['', 'Association', 'Authentication', 'DHCP', 'DNS', 'Success'],
        datasets: [{
            data: [0, 0, 0, 0, 0, 0],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                },
                scaleLabel: {
                    display: true,
                    labelString: "% of clients succeeding at this step"
                }
            }]
        },
        elements: {
            line: {
                tension: 0
            }
        }
    }
});

var current_assoc = 0;
var current_auth = 0;
var current_dhcp = 0;
var current_dns = 0;
var current_success = 0;

function updateChart(){
    assoc = current_success - current_assoc;
    auth = assoc - current_auth;
    dhcp = auth - current_dhcp;
    dns = dhcp - current_dns;
    success = dns;

    assoc = assoc / current_success * 100;
    auth = auth / current_success * 100;
    dhcp = dhcp / current_success * 100;
    dns = dns / current_success * 100;
    success = success / current_success * 100;

    myChart.data.datasets[0].data[0] = 100;
    myChart.data.datasets[0].data[1] = assoc;
    myChart.data.datasets[0].data[2] = auth;
    myChart.data.datasets[0].data[3] = dhcp;
    myChart.data.datasets[0].data[4] = dns;
    myChart.data.datasets[0].data[5] = success;
    myChart.update();
    $('#loader').hide();
}

function get_networks(org_id){
    $.ajax({
        type: 'GET',
        url: `/get_networks/${org_id}`,
        success: function(nets){
            $('#select-net').html("<option value=\"null\">Select a Network</option>");
            JSON.parse(nets).forEach((net, n) => {
                $('#select-net').append(`<option value=${net.id}>${net.name}</option>`);
            });
        }
    });
}

function toggle_reasons(e){
    if($(e).is(":checked")){
        if($(e).data("failuretype") == "assoc"){
            current_assoc += $(e).data("count");
        }else if($(e).data("failuretype") == "auth"){
            current_auth += $(e).data("count");
        }else if($(e).data("failuretype") == "dhcp"){
            current_dhcp += $(e).data("count");
        }else if($(e).data("failuretype") == "dns"){
            current_dns += $(e).data("count");
        }
    }else{
      if($(e).data("failuretype") == "assoc"){
          current_assoc -= $(e).data("count");
      }else if($(e).data("failuretype") == "auth"){
          current_auth -= $(e).data("count");
      }else if($(e).data("failuretype") == "dhcp"){
          current_dhcp -= $(e).data("count");
      }else if($(e).data("failuretype") == "dns"){
          current_dns -= $(e).data("count");
      }
    }
    updateChart();
}

function populate_reasons(failures){
    var reasons = {};
    failures.forEach((failure, f) => {
        if(!(failure[1] in reasons)){
            reasons[failure[1]] = {};
        }
        if([failure[2]] in reasons[failure[1]]){
            reasons[failure[1]][failure[2]]++;
        }else{
            reasons[failure[1]][failure[2]] = 1;
        }
    });

    current_assoc = 0;
    current_auth = 0;
    current_dhcp = 0;
    current_dns = 0;

    var reasons_html = "";
    for(let [failureType, reason] of Object.entries(reasons)){
        reasons_html += `<div class="col-lg-4 col-md-4 col-4"><div class="subheader">${failureType.toUpperCase()}</div>`;
        totalc = 0;
        for(let [detail, c] of Object.entries(reason)){
            reasons_html += `<div class="form-group form-group--inline"><label class="checkbox"><input type="checkbox" checked data-failuretype="${failureType}" data-count="${c}" onchange="toggle_reasons(this)"><span class="checkbox__input"></span><span class="checkbox__label">${detail} (${c})</span></label></div>`;
            totalc += c;
        }
        reasons_html += "</div>";

        if(failureType == 'assoc'){
            current_assoc = totalc;
        }else if(failureType == 'auth'){
            current_auth = totalc;
        }else if(failureType == 'dhcp'){
            current_dhcp = totalc;
        }else if(failureType == 'dns'){
            current_dns = totalc;
        }
    }

    $('#reasons').html(reasons_html);
}

function get_wireless_health(){
    $('#loader').show();
    net_id = $('#select-net').val();
    start_date = $('#start-date').val();
    end_date = $('#end-date').val();

    $.ajax({
        type: 'GET',
        url: `/get_wireless_health/${net_id}/${start_date}/${end_date}`,
        success: function(data){
            data = JSON.parse(data);
            console.log(data);
            current_success = data['success'];
            populate_reasons(data['failedClients']);
            updateChart();
        }
    });
}