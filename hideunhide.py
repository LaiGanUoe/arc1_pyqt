def hide_unhide(self, v):
    if v == 'Retention' and self.hidden:
        self.every_dropDown.show()
        self.duration_dropDown.show()
        self.lineEdit_every.show()
        self.lineEdit_duration.show()
        self.every_label.show()
        self.duration_label.show()
        self.hidden = False

    else:
        self.every_dropDown.hide()
        self.duration_dropDown.hide()
        self.lineEdit_every.hide()
        self.lineEdit_duration.hide()
        self.every_label.hide()
        self.duration_label.hide()
        # self.switch_seek.hide()
        self.hidden = True

    if v == 'Switch Seeker' and self.hidden:
        self.switch_seek1.show()
        self.switch_seek2.show()
        self.switch_seek3.show()
        self.switch_seek4.show()
        self.switch_seek5.show()
        self.switch_seek6.show()
        self.switch_seek7.show()
        self.switch_seek8.show()
        self.switch_seek9.show()
        self.switch_seek10.show()
        self.switch_seek1_label.show()
        self.switch_seek2_label.show()
        self.switch_seek3_label.show()
        self.switch_seek4_label.show()
        self.switch_seek5_label.show()
        self.switch_seek6_label.show()
        self.switch_seek7_label.show()
        self.switch_seek8_label.show()
        self.switch_seek9_label.show()
        self.switch_seek10_label.show()
        self.switch_seek_combo1_label.show()
        self.switch_seek_combo1.show()
        self.switch_seek_combo2_label.show()
        self.switch_seek_combo2.show()
        self.CB_skip_stage1.show()
        self.CB_skip_stage1_label.show()
        self.CB_read_after.show()
        self.CB_read_after_label.show()

        self.hidden = False
    else:
        self.switch_seek1.hide()
        self.switch_seek2.hide()
        self.switch_seek3.hide()
        self.switch_seek4.hide()
        self.switch_seek5.hide()
        self.switch_seek6.hide()
        self.switch_seek7.hide()
        self.switch_seek8.hide()
        self.switch_seek9.hide()
        self.switch_seek10.hide()
        self.switch_seek1_label.hide()
        self.switch_seek2_label.hide()
        self.switch_seek3_label.hide()
        self.switch_seek4_label.hide()
        self.switch_seek5_label.hide()
        self.switch_seek6_label.hide()
        self.switch_seek7_label.hide()
        self.switch_seek8_label.hide()
        self.switch_seek9_label.hide()
        self.switch_seek10_label.hide()
        self.switch_seek_combo1_label.hide()
        self.switch_seek_combo1.hide()
        self.switch_seek_combo2_label.hide()
        self.switch_seek_combo2.hide()
        self.CB_skip_stage1.hide()
        self.CB_skip_stage1_label.hide()
        self.CB_read_after.hide()
        self.CB_read_after_label.hide()

        self.hidden = True

    if v == 'Form Finder' and self.hidden:
        self.form_finder1.show()
        self.form_finder2.show()
        self.form_finder3.show()
        self.form_finder4.show()
        self.form_finder5.show()
        self.form_finder6.show()
        self.form_finder7.show()
        self.form_finder8.show()
        self.form_finder9.show()
        self.form_finder10.show()
        self.form_finder1_label.show()
        self.form_finder2_label.show()
        self.form_finder3_label.show()
        self.form_finder4_label.show()
        self.form_finder5_label.show()
        self.form_finder6_label.show()
        self.form_finder7_label.show()
        self.form_finder8_label.show()
        self.form_finder9_label.show()
        self.form_finder10_label.show()
        self.form_finder_combo1_label.show()
        self.form_finder_combo1.show()
        self.form_finder_combo2_label.show()
        self.form_finder_combo2.show()
        self.CB_form_finder1.show()
        self.CB_form_finder1_label.show()
        self.CB_form_finder2.show()
        self.CB_form_finder2_label.show()

        self.hidden = False

    else:
        self.form_finder1.hide()
        self.form_finder2.hide()
        self.form_finder3.hide()
        self.form_finder4.hide()
        self.form_finder5.hide()
        self.form_finder6.hide()
        self.form_finder7.hide()
        self.form_finder8.hide()
        self.form_finder9.hide()
        self.form_finder10.hide()
        self.form_finder1_label.hide()
        self.form_finder2_label.hide()
        self.form_finder3_label.hide()
        self.form_finder4_label.hide()
        self.form_finder5_label.hide()
        self.form_finder6_label.hide()
        self.form_finder7_label.hide()
        self.form_finder8_label.hide()
        self.form_finder9_label.hide()
        self.form_finder10_label.hide()
        self.form_finder_combo1_label.hide()
        self.form_finder_combo1.hide()
        self.form_finder_combo2_label.hide()
        self.form_finder_combo2.hide()
        self.CB_form_finder1.hide()
        self.CB_form_finder1_label.hide()
        self.CB_form_finder2.hide()
        self.CB_form_finder2_label.hide()
        self.hidden = True

    if v == 'Converge' and self.hidden:
        self.converge1.show()
        self.converge_combo1.show()
        self.converge3.show()
        self.converge4.show()
        self.converge5.show()
        self.converge6.show()
        self.converge7.show()
        self.converge8.show()
        self.converge9.show()
        self.converge10.show()
        self.converge11.show()
        self.converge12.show()
        self.converge1_label.show()
        self.converge_combo1_label.show()
        self.converge3_label.show()
        self.converge4_label.show()
        self.converge5_label.show()
        self.converge6_label.show()
        self.converge7_label.show()
        self.converge8_label.show()
        self.converge9_label.show()
        self.converge10_label.show()
        self.converge11_label.show()
        self.converge12_label.show()
        self.hidden = False
    else:
        self.converge1.hide()
        self.converge_combo1.hide()
        self.converge3.hide()
        self.converge4.hide()
        self.converge5.hide()
        self.converge6.hide()
        self.converge7.hide()
        self.converge8.hide()
        self.converge9.hide()
        self.converge10.hide()
        self.converge1_label.hide()
        self.converge_combo1_label.hide()
        self.converge3_label.hide()
        self.converge4_label.hide()
        self.converge5_label.hide()
        self.converge6_label.hide()
        self.converge7_label.hide()
        self.converge8_label.hide()
        self.converge9_label.hide()
        self.converge10_label.hide()
        self.converge11.hide()
        self.converge12.hide()
        self.converge11_label.hide()
        self.converge12_label.hide()
        self.hidden = True
    if v=='CurveTracer' and self.hidden:
        self.curvetracer1.show()
        self.curvetracer2.show()
        self.curvetracer3.show()
        self.curvetracer4.show()
        self.curvetracer5.show()
        self.curvetracer6.show()
        self.curvetracer7.show()
        self.curvetracer8.show()
        self.curvetracer9.show()
        self.curvetracer10.show()
        self.curvetracer1_label.show()
        self.curvetracer2_label.show()
        self.curvetracer3_label.show()
        self.curvetracer4_label.show()
        self.curvetracer5_label.show()
        self.curvetracer6_label.show()
        self.curvetracer7_label.show()
        self.curvetracer8_label.show()
        self.curvetracer9_label.show()
        self.curvetracer10_label.show()
        self.curvetracer_combo1_label.show()
        self.curvetracer_combo1.show()
        self.curvetracer_combo2_label.show()
        self.curvetracer_combo2.show()
        self.CB_curvetracer1.show()
        self.CB_curvetracer1_label.show()
        self.CB_curvetracer2.show()
        self.CB_curvetracer2_label.show()
        
        self.hidden = False
    else:
        self.curvetracer1.hide()
        self.curvetracer2.hide()
        self.curvetracer3.hide()
        self.curvetracer4.hide()
        self.curvetracer5.hide()
        self.curvetracer6.hide()
        self.curvetracer7.hide()
        self.curvetracer8.hide()
        self.curvetracer9.hide()
        self.curvetracer10.hide()
        self.curvetracer1_label.hide()
        self.curvetracer2_label.hide()
        self.curvetracer3_label.hide()
        self.curvetracer4_label.hide()
        self.curvetracer5_label.hide()
        self.curvetracer6_label.hide()
        self.curvetracer7_label.hide()
        self.curvetracer8_label.hide()
        self.curvetracer9_label.hide()
        self.curvetracer10_label.hide()
        self.curvetracer_combo1_label.hide()
        self.curvetracer_combo1.hide()
        self.curvetracer_combo2_label.hide()
        self.curvetracer_combo2.hide()
        self.CB_curvetracer1.hide()
        self.CB_curvetracer1_label.hide()
        self.CB_curvetracer2.hide()
        self.CB_curvetracer2_label.hide()
        self.hidden = True
        
    if v=='ParameterFit' and self.hidden:
        self.parameterfit1.show()
        self.parameterfit2.show()
        self.parameterfit3.show()
        self.parameterfit4.show()
        self.parameterfit5.show()
        self.parameterfit6.show()
        self.parameterfit7.show()
        self.parameterfit8.show()
        self.parameterfit9.show()
        self.parameterfit10.show()
        self.parameterfit1_label.show()
        self.parameterfit2_label.show()
        self.parameterfit3_label.show()
        self.parameterfit4_label.show()
        self.parameterfit5_label.show()
        self.parameterfit6_label.show()
        self.parameterfit7_label.show()
        self.parameterfit8_label.show()
        self.parameterfit9_label.show()
        self.parameterfit10_label.show()
        self.CB_parameterfit1.show()
        self.CB_parameterfit1_label.show()
        self.hidden = False
    else:
        self.parameterfit1.hide()
        self.parameterfit2.hide()
        self.parameterfit3.hide()
        self.parameterfit4.hide()
        self.parameterfit5.hide()
        self.parameterfit6.hide()
        self.parameterfit7.hide()
        self.parameterfit8.hide()
        self.parameterfit9.hide()
        self.parameterfit10.hide()
        self.parameterfit1_label.hide()
        self.parameterfit2_label.hide()
        self.parameterfit3_label.hide()
        self.parameterfit4_label.hide()
        self.parameterfit5_label.hide()
        self.parameterfit6_label.hide()
        self.parameterfit7_label.hide()
        self.parameterfit8_label.hide()
        self.parameterfit9_label.hide()
        self.parameterfit10_label.hide()
        self.CB_parameterfit1.hide()
        self.CB_parameterfit1_label.hide()
        self.hidden = True

    if v=='RILForming' and self.hidden:
        self.RILForming1.show()
        self.RILForming2.show()
        self.RILForming3.show()
        self.RILForming4.show()
        self.RILForming5.show()

        self.RILForming1_label.show()
        self.RILForming2_label.show()
        self.RILForming3_label.show()
        self.RILForming4_label.show()
        self.RILForming5_label.show()


        self.hidden = False
    else:
        self.RILForming1.hide()
        self.RILForming2.hide()
        self.RILForming3.hide()
        self.RILForming4.hide()
        self.RILForming5.hide()

        self.RILForming1_label.hide()
        self.RILForming2_label.hide()
        self.RILForming3_label.hide()
        self.RILForming4_label.hide()
        self.RILForming5_label.hide()


        self.hidden = True
        
    if v=='Uniformity' and self.hidden:
        self.uniformity1.show()
        self.CB_uniformity2.show()
        self.CB_uniformity3.show()
        self.uniformity4.show()
        self.uniformity5.show()
        
        self.uniformity1_label.show()
        self.CB_uniformity2_label.show()
        self.CB_uniformity3_label.show()
        self.uniformity4_label.show()
        self.uniformity5_label.show()
        

        self.hidden = False
    else:
        self.uniformity1.hide()
        self.CB_uniformity2.hide()
        self.CB_uniformity3.hide()
        self.uniformity4.hide()
        self.uniformity5.hide()
        self.uniformity1_label.hide()
        self.CB_uniformity2_label.hide()
        self.CB_uniformity3_label.hide()
        self.uniformity4_label.hide()
        self.uniformity5_label.hide()
        
        
        
        self.hidden = True