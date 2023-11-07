"""
TODO
- Replace all path to absolute path     : Pending
"""

def fill_data(
        gui_object = None,
        meta_data  = {}
):
    """
        DESCRIPTION:
            Read the meta data and fill all the gui labels and texts.
    """

    print("Fill data function started.")

    gui_object.actuator_sno_lineedit.setPlainText(meta_data['actuator_serial_number'])
    gui_object.document_no_label.setText("Document number: " + meta_data['document_number'])
    gui_object.revision_no_label.setText("Revision number: " + meta_data['revision_number'])

    gui_object.assembled_by_name.setText(meta_data['assembler_name'])
    gui_object.assembled_by_date.setText(meta_data['assembly_date'])
    gui_object.assembled_by_signature.setText(meta_data['assembler_signature'])
    gui_object.tested_by_name.setText(meta_data['tester_name'])
    gui_object.tested_by_date.setText(meta_data['testing_date'])
    gui_object.tested_by_signature.setText(meta_data['tester_signature'])
    gui_object.approved_by_name.setText(meta_data['approver_name'])
    gui_object.approved_by_date.setText(meta_data['approval_date'])
    gui_object.approved_by_signature.setText(meta_data['approver_signature'])
    gui_object.end_remark_lineedit.setPlainText(meta_data['end_remarks'])

    for i,checkbox in enumerate(gui_object.checklist_checkboxes):
        # change the checkbox status
        if meta_data['ch_{}'.format(i + 1)] == u'\u2713':
            checkbox.setChecked(True)
        elif meta_data['ch_{}'.format(i + 1)] == u'\u2717':
            checkbox.setChecked(False)
            
    for i,combobox in enumerate(gui_object.yes_no_combobox):
        # change the combobox status
        if meta_data['yn_{}'.format(i+1)] == "yes":
            combobox.setCurrentText("yes")
        elif meta_data['yn_{}'.format(i+1)] == "no":
            combobox.setCurrentText("no")

    for i,plainTextEdit in enumerate(gui_object.checklist_lineedits):
        # change remarks text
        plainTextEdit.setPlainText(meta_data['remarks_{}'.format(i+1)])

    gui_object.yes_no_linedits[0].setPlainText(meta_data['inspector_name_1'] )
    gui_object.yes_no_linedits[1].setPlainText(meta_data['inspector_name_2'] )

    return None