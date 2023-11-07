import datetime as dt

"""
TODO
- Replace all path to absolute path     : Pending
"""

def make_meta_data(
        gui_object,
        default = False
):
    
    default_meta_data = {
        'actuator_serial_number'            : "No serial no found",
        'document_number'                   : "No document no found",
        'revision_number'                   : "No revision no  found",
        'date'                              : "No date found",
        'assembler_name'                    : "No name found",
        'assembly_date'                     : "No date found",
        'assembler_signature'               : "No signature found",
        'tester_name'                       : "No name found",
        'testing_date'                      : "No date found",
        'tester_signature'                  : "No signature found",
        'approver_name'                     : "No name found",
        'approval_date'                     : "No date found",
        'approver_signature'                : "No signature found",
        'end_remarks'                       : "No remarks found",
        'ch_1'                              : u'\u2717',
        'ch_2'                              : u'\u2717',
        'ch_3'                              : u'\u2717',
        'ch_4'                              : u'\u2717',
        'ch_5'                              : u'\u2717',
        'ch_6'                              : u'\u2717',
        'ch_7'                              : u'\u2717',
        'ch_8'                              : u'\u2717',
        'yn_1'                              : "No data found",
        'yn_2'                              : "No data found",
        'remarks_1'                         : "",
        'remarks_2'                         : "",
        'remarks_3'                         : "",
        'remarks_4'                         : "",   
        'remarks_5'                         : "",
        'remarks_6'                         : "",
        'inspector_name_1'                  : "",
        'inspector_name_2'                  : "",
    }

    meta_data = {}

    meta_data['actuator_serial_number'] = gui_object.actuator_sno_lineedit.toPlainText()
    # set document number, need to do changes in gui
    meta_data['document_number']        = gui_object.document_no_label.text()[17:]
    #meta_data['document_number']        = default_meta_data['document_number']
    # set revision number, need to do changes in gui
    meta_data['revision_number']        = gui_object.revision_no_label.text()[20:]
    #meta_data['revision_number']        = default_meta_data['revision_number']

    date_format = "%d-%m-%Y" 
    date_now    = dt.datetime.now().strftime(format=date_format)

    meta_data['date']                   = date_now

    meta_data['assembler_name']         = gui_object.assembled_by_name.text()
    meta_data['assembly_date']          = gui_object.assembled_by_date.text()
    meta_data['assembler_signature']    = gui_object.assembled_by_signature.text()
    meta_data['tester_name']            = gui_object.tested_by_name.text()
    meta_data['testing_date']           = gui_object.tested_by_date.text()
    meta_data['tester_signature']       = gui_object.tested_by_signature.text()
    meta_data['approver_name']          = gui_object.approved_by_name.text()
    meta_data['approval_date']          = gui_object.approved_by_date.text()
    meta_data['approver_signature']     = gui_object.approved_by_signature.text()
    meta_data['end_remarks']            = gui_object.end_remark_lineedit.toPlainText()


    for i,checkbox in enumerate(gui_object.checklist_checkboxes):
        if checkbox.isChecked():
            meta_data['ch_{}'.format(i + 1)] = u'\u2713'
        else:
            meta_data['ch_{}'.format(i + 1)] = u'\u2717'
    
    for i,combobox in enumerate(gui_object.yes_no_combobox):
        meta_data['yn_{}'.format(i+1)] = combobox.currentText()

    for i,plainTextEdit in enumerate(gui_object.checklist_lineedits):
        meta_data['remarks_{}'.format(i+1)] = plainTextEdit.toPlainText()

    meta_data['inspector_name_1']           = gui_object.yes_no_linedits[0].toPlainText()
    meta_data['inspector_name_2']           = gui_object.yes_no_linedits[1].toPlainText()

    if default:
        meta_data = default_meta_data
    
    return meta_data