export function generateHtml(json_obj) {

    let stock_array = Object.values(json_obj);
    stock_array.sort(function (a, b) {
        return a.comment.conclusion.localeCompare(b.comment.conclusion);
    });

    let web_content = `<table><tr><th>Stock Now</th><th>Mid-Term</th><th>Health Check</th></tr>`;

    for (let i = 0; i < stock_array.length; i++) {
        let stock_json = stock_array[i].comment;
        let shortName = stock_json['short_name'];
        let conclusion = stock_json['conclusion'];
        let trend_2 = stock_json['TREND_2'];

        let status_code = conclusion.substring(0, 1);
        let the_css = '';
        let icon = '';
        let trend_2_icon = (trend_2.startsWith('Downward')) ? 'trending_down' : 'trending_up';

        switch (status_code) {
            case '0':
                the_css = 'verygood';
                icon = 'star';
                break;
            case '1':
                the_css = 'good';
                icon = 'child_care';
                break;
            case '2':
                the_css = 'watch';
                icon = 'sentiment_satisfied';
                break;
            case '3':
                the_css = 'bad';
                icon = 'sentiment_very_dissatisfied';
                break;
            default:
                icon = 'sentiment_neutral';
                break;
        }
        web_content += `<tr>
                <td class=${the_css}><i class="material-icons md-18" >${icon}</i>${shortName}</td>
                <td><i class="material-icons md-18" >${trend_2_icon}</i></td>
                <td>${conclusion.substring(4)}</td></tr>`;
    }
    web_content += `</table>`;

    return web_content;
}
