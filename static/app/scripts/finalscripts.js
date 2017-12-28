/*
 * Definition of Javascript functions;
 * Used for partial page refresh with AJAX
*/

///// Search Recore functions

function getSearchForm(formType) {
    $.ajax({
        type: "GET",
        url: 'getSearchForm',
        data: { 'formType': formType }
    })
        .done(function (response) {
            $('#getSearchForm_JS').replaceWith(response);
        });
};

function retrofitAttr_jscript(equipType) {
    $.ajax({
        type: "GET",
        url: 'retrofitAttr',
        data: { 'equip': equipType }
    })
        .done(function (response) {
            $('#retrofitAttr_JS').replaceWith(response);
        });
}

function getKioskForm_jscript(formType) {
    $.ajax({
        type: "GET",
        url: 'getKioskModelForm',
        data: { 'formType': formType }
    })
        .done(function (response) {
            $('#updateDatabase_getForm_JS').replaceWith(response);
        });
};

function createKioskModel_jscript(kioskType, ctsDivision) {
    $.ajax({
        type: "GET",
        url: 'createKioskModel',
        data: { 'kioskType': kioskType, 'ctsDivision': ctsDivision }
    })
        .done(function (response) {
            $('#updateDatabase_getForm_JS').replaceWith(response);
        });
};

///// Production Release functions

function newProdRlseEquip_jscript(equipList, compList, nextComp, kioskType) {
    $.ajax({
        type: "GET",
        url: 'newProdRlseEquip',
        traditional: true,
        data: { 'equipList': equipList, 'compList': compList, 'nextComp': nextComp, 'kioskType': kioskType }
    })
        .done(function (response) {
            $(nextComp).replaceWith(response);
        });
};

function getSubEquip_jscript(currentEquip, subEquipDiv) {
    $.ajax({
        type: "GET",
        url: 'getSubEquip',
        data: { 'currentEquip': currentEquip, 'subEquipDiv': subEquipDiv }
    })
        .done(function (response) {
            $(subEquipDiv).replaceWith(response);
        });
};

function resetProdRlse_jscript(currentDiv) {
    $.ajax({
        type: "GET",
        url: 'resetProdRlse',
        data: { 'currentDiv': currentDiv }
    })
        .done(function (response) {
            $(currentDiv).replaceWith(response);
        });
};

function addEquipList(currentEquip, newComp, nextComp, kioskType) {
    currentComp = newComp.substr(1);

    if (compDict[currentComp].length > 0) {
        for (i = allComp.indexOf(currentComp); i < allComp.length; i++) {
            compDict[allComp[i]].splice(0);
            resetProdRlse_jscript('#'.concat(allComp[i+1]));
            resetProdRlse_jscript('#'.concat(allComp[i+1]).concat('A'));
        }
    }

    compDict[currentComp].push(currentEquip);

    var allEquip = [];
    for (var comp in compDict) {
        var tempArray = compDict[comp];
        for (i = 0; i < tempArray.length; i++) {
            allEquip.push(tempArray[i]);
        }
    }

    subEquipDiv = newComp.concat('A');
    getSubEquip_jscript(currentEquip, subEquipDiv);
    newProdRlseEquip_jscript(allEquip, allComp, nextComp, kioskType);
}

function addEquipListCheckbox(checkbox, newComp, nextComp, newEquip, kioskType) {
    if (checkbox.checked == true) {
        currentEquip = checkbox.value;

        currentComp = newComp.substr(1);
        compDict[currentComp].push(currentEquip);

        var allEquip = [];
        for (var comp in compDict) {
            var tempArray = compDict[comp];
            for (i = 0; i < tempArray.length; i++) {
                allEquip.push(tempArray[i]);
            }
        }

        subEquipDiv = newEquip.concat('D');
        getSubEquip_jscript(currentEquip, subEquipDiv)
    }

    else {
        currentEquip = checkbox.value;

        currentComp = newComp.substr(1);
        var tempIndex = compDict[currentComp].indexOf(currentEquip);
        compDict[currentComp].splice(tempIndex, 1);

        for (i = allComp.indexOf(currentComp) + 1; i < allComp.length; i++) {
            compDict[allComp[i]].splice(0);
            resetProdRlse_jscript('#'.concat(allComp[i]));
            resetProdRlse_jscript('#'.concat(allComp[i]).concat('A'));
            resetProdRlse_jscript(newEquip.concat('D'));
        }

        getNextComp(nextComp, kioskType);
    }
}

function getNextComp(nextComp, kioskType) {
    var allEquip = [];
    for (var comp in compDict) {
        var tempArray = compDict[comp];
        for (i = 0; i < tempArray.length; i++) {
            allEquip.push(tempArray[i]);
        }
    }

    newProdRlseEquip_jscript(allEquip, allComp, nextComp, kioskType)
}

function existingSubequip_jscript(currentEquip) {
    $.ajax({
        type: "GET",
        url: 'existingSubequip',
        data: { 'currentEquip': currentEquip }
    })
        .done(function (response) {
            $(currentEquip).replaceWith(response);
        });
};


function editProdRlseInfo_jscript(jobNumber) {
    $.ajax({
        type: "GET",
        url: 'editProdRlseInfo',
        data: { 'jobNumber': jobNumber }
    })
        .done(function (response) {
            $('#editProdRlseInfo_JS').replaceWith(response);
        });
};


function editProdRlseEquip_jscript(jobNumber) {
    $.ajax({
        type: "GET",
        url: 'editProdRlseEquip',
        data: { 'jobNumber': jobNumber }
    })
        .done(function (response) {
            $('#editProdRlseEquip_JS').replaceWith(response);
        });
};

function editExistSubequip(equipID, compID, jobNumber) {
    var equip = document.getElementById(equipID).value;

    $.ajax({
        type: "GET",
        url: 'editExistSubequip',
        data: { 'equip': equip, 'comp': compID, 'jobNumber': jobNumber }
    })
        .done(function (response) {
            $(compID).replaceWith(response);
        });
};

function editExistEquipList(currentEquip, newComp, nextComp, kioskType) {
    currentComp = newComp.substr(1);
    compDict[currentComp].splice(0);
    compDict[currentComp].push(currentEquip);

    var allEquip = [];
    for (var comp in compDict) {
        var tempArray = compDict[comp];
        for (i = 0; i < tempArray.length; i++) {
            allEquip.push(tempArray[i]);
        }
    }

    $.ajax({
        type: "GET",
        url: 'checkExistEquipRestrict',
        data: { 'equip': currentEquip }
    })
        .done(function (response) {
            if (response == 1) {
                for (i = allComp.indexOf(currentComp); i < allComp.length; i++) {
                    compDict[allComp[i]].splice(0);
                    resetProdRlse_jscript('#'.concat(allComp[i + 1]));
                    resetProdRlse_jscript('#'.concat(allComp[i + 1]).concat('A'));
                }
                subEquipDiv = newComp.concat('A');
                getSubEquip_jscript(currentEquip, subEquipDiv);
                newProdRlseEquip_jscript(allEquip, allComp, nextComp, kioskType);
            }
            else {
                subEquipDiv = newComp.concat('A');
                getSubEquip_jscript(currentEquip, subEquipDiv);
            }
        });
};

function editExistEquipCheckbox(checkbox, newComp, nextComp, newEquip, kioskType) {
    if (checkbox.checked == true) {
        currentEquip = checkbox.value;

        currentComp = newComp.substr(1);
        compDict[currentComp].push(currentEquip);

        var allEquip = [];
        for (var comp in compDict) {
            var tempArray = compDict[comp];
            for (i = 0; i < tempArray.length; i++) {
                allEquip.push(tempArray[i]);
            }
        }

        subEquipDiv = newEquip.concat('F');
        getSubEquip_jscript(currentEquip, subEquipDiv)
    }

    else {
        currentEquip = checkbox.value;

        currentComp = newComp.substr(1);
        var tempIndex = compDict[currentComp].indexOf(currentEquip);
        compDict[currentComp].splice(tempIndex, 1);

        $.ajax({
            type: "GET",
            url: 'checkExistEquipRestrict',
            data: { 'equip': currentEquip }
        })
            .done(function (response) {
                if (response == 1) {
                    for (i = allComp.indexOf(currentComp) + 1; i < allComp.length; i++) {
                        compDict[allComp[i]].splice(0);
                        resetProdRlse_jscript('#'.concat(allComp[i]));
                        resetProdRlse_jscript('#'.concat(allComp[i]).concat('A'));
                        resetProdRlse_jscript(newEquip.concat('F'));
                    }
                }
                else {
                    resetProdRlse_jscript(newEquip.concat('F'));
                }

                //getNextComp(nextComp, kioskType);
            });
    };
}

///// End Production Release functions

/////

///// Update Database functions

function getDatabaseForm_jscript(formType) {
    $.ajax({
        type: "GET",
        url: 'getDatabaseForm',
        data: { 'formType': formType }
    })
        .done(function (response) {
            $('#getDatabaseForm_JS').replaceWith(response);
        });
};

function addNewEquip_jscript(prod, comp, equipDiv) {
    $.ajax({
        type: "GET",
        url: 'kioskModelNewEquip',
        data: { 'prod': prod, 'comp': comp, 'equipDiv': equipDiv }
    })
        .done(function (response) {
            $(equipDiv).replaceWith(response);
        });
};

function getEquipValues(prod, comp) {
    var make = document.getElementById("make_id").value;
    var model = document.getElementById("model_id").value;
    var equip_descript = document.getElementById("equip_descript_id").value;
    var ctsNumber = document.getElementById("ctsNumber_id").value;
    var manfNumber = document.getElementById("manfNumber_id").value;

    if ((make != "") && (model != "") && (equip_descript != "")) {
        createNewEquip_jscript(prod, comp, make, model, equip_descript, ctsNumber, manfNumber);
    }
};

function createNewEquip_jscript(prod, comp, make, model, equip_descript, ctsNumber, manfNumber) {
    $.ajax({
        type: "GET",
        url: 'kioskModelCreateEquip',
        data: { 'prod': prod, 'comp': comp, 'make': make, 'model': model, 'equip_descript': equip_descript, 'ctsNumber': ctsNumber, 'manfNumber': manfNumber }
    })
        .done(function (response) {
            $('#createKioskRelations_JS').replaceWith(response);
        });
};

function addNewComp_jscript(prod, compDiv) {
    $.ajax({
        type: "GET",
        url: 'kioskModelNewComp',
        data: { 'prod': prod, 'compDiv': compDiv }
    })
        .done(function (response) {
            $(compDiv).replaceWith(response);
        });
};

function getCompValues(prod) {
    var name = document.getElementById("name_id").value;
    var display_type = $("input:radio[name='display_type']:checked").val();
    var comp_descript = document.getElementById("comp_descript_id").value;

    if ((name != "") && (display_type != "") && (comp_descript != "")) {
        createNewComp_jscript(prod, name, display_type, comp_descript);
    }
};

function createNewComp_jscript(prod, name, display_type, comp_descript) {
    $.ajax({
        type: "GET",
        url: 'kioskModelCreateComp',
        data: { 'prod': prod, 'name': name, 'display_type': display_type, 'comp_descript': comp_descript }
    })
        .done(function (response) {
            $('#createKioskRelations_JS').replaceWith(response);
        });
};

function addNewProd_jscript() {
    $.ajax({
        type: "GET",
        url: 'kioskModelNewProd',
        data: {}
    })
        .done(function (response) {
            $('#addNewProd_JS').replaceWith(response);
        });
};

function getProdValues() {
    var name = document.getElementById("name_id").value;
    var prod_descript = document.getElementById("prod_descript_id").value;

    if ((name != "") && (prod_descript != "")) {
        createNewProd_jscript(name, prod_descript);
    }
};

function createNewProd_jscript(name, prod_descript) {
    $.ajax({
        type: "GET",
        url: 'kioskModelCreateProd',
        data: { 'name': name, 'prod_descript': prod_descript }
    })
        .done(function (response) {
            $('#createKioskRelations_JS').replaceWith(response);
        });
};
/*
function createKioskRelations_jscript() {
    $.ajax({
        type: "GET",
        url: 'createKioskRelations',
        data: { }
    })
        .done(function (response) {
            $('#createKioskRelations_JS').replaceWith(response);
        });
};
*/
function getNewRelations_jscript(currentKioskType) {
    var newEquipRelation = []
    $("input[name='equipRelationList[]']:checked").each(function () {
        newEquipRelation.push(parseInt($(this).val()));
    });

    $.ajax({
        type: "GET",
        url: 'newEquipRelations',
        data: { 'equipRelations': newEquipRelation, 'currentKioskType': currentKioskType }
    })
        .done(function (response) {
            $('#newEquipRelations_JS').replaceWith(response);
        });
};

function cancelDatabaseForm_jscript() {
    $.ajax({
        type: "GET",
        url: 'cancelDatabaseForm',
        data: {}
    })
        .done(function (response) {
            $('#createKioskRelations_JS').replaceWith(response);
        });
};

///// End Update Database functions