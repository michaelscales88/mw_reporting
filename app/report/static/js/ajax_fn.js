function buildAjaxData() {
    let settings = $("#displayTable").dataTable().fnSettings();

    let obj = {
        //default params
        "draw": settings.iDraw,
        "start": settings._iDisplayStart,
        "length": settings._iDisplayLength,
        "columns": "",
        "order": "",

        "action": sessionStorage.action,
        "report_range": $('input[name="report_range"]').val()
    };
    console.log('Ajax page');
    console.log(sessionStorage.action);
    //building the columns
    let col = []; // array

    for (let index in settings.aoColumns) {
        let data = settings.aoColumns[index];
        col.push(data.sName);

    }

    let ord = {
        "column": settings.aLastSort[0].col,
        "dir": settings.aLastSort[0].dir
    };

    //assigning
    obj.columns = col;
    obj.order = ord;

    return obj;
}