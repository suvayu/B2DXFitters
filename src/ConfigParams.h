#ifndef __CONFIGPARAMS_H__
#define __CONFIGPARAMS_H__

#include <TString.h>

class ConfigParams {
  public :

    // ===================================================================================================================================
    // Start variable definition
    // ===================================================================================================================================
    
    bool    debug_mode, verbose_mode;
    TString m_suffix;
   
    // Parameters for the ToyMC generator and fitter
   
    int     numdkids;
  
    double  mutogen;
    
    double  lowerswimrange;
    double  upperswimrange;		
    double  swimgranularity;		
    double  swimratio;			
    int     swimiters;			
    
    double  b_lifetime;
    double  b_lifetime_res;
    double  b_mass;
    double  b_mass_res;
    double  b_child_masses[2];
    
    double  d_lifetime;
    double  d_mass;
    double  d_mass_res;
    double  d_child_masses[3];
    
    double  combo_lifetime;
    double  combo_mass_low;		
    double  combo_mass_high;
    double  combo_child_masses[4];
    
    double  track_eff_const;
    double  track_eff_slope;
    
    double  beta_factor;
    
    double  trig_pt_cut_2body;
    double  trig_pt_cut_3body;
    double  trig_ip_cut_2body;
    double  trig_ip_cut_3body;
   
    int     num_event_types; 
    double  event_compositions[2];
    double  event_lifetime[2];
    int     event_color[2];
    TString event_names[2];
  
    TString examplefit_filename;
    TString pull_filename;
 
    // Plotting options
    int     model_prec;
    double  event_yield;

    // Data fit options
    TString datafit_filename;
 
    ConfigParams(){
  
      //Parameters for the ToyMC generator and fitter
  
      debug_mode		= false;
      verbose_mode		= false;
      m_suffix			= "";      
      
      mutogen			= 2.;
  
      numdkids 			= 3;
      
      lowerswimrange		= 0.;
      upperswimrange		= 50.;
      swimgranularity		= 0.5;
      swimratio			= 10.;
      swimiters			= 3;
      
      b_lifetime 		= 1.5;
      b_lifetime_res 		= 0.050;
      b_mass 			= 5369.;
      b_mass_res		= 20.;
      b_child_masses[0]		= 1969.;
      b_child_masses[1]		= 139.57;
      
      d_lifetime 		= 0.400;
      d_mass 			= 1969.;
      d_mass_res		= 8.;
      d_child_masses[0]		= 493.67;
      d_child_masses[1]		= 493.67;
      d_child_masses[2]		= 139.57;
      
      combo_lifetime		= 0.400;
      combo_mass_low		= 5100.;
      combo_mass_high		= 5600.;
      combo_child_masses[0]	= 139.57;
      combo_child_masses[1]	= 493.67;
      combo_child_masses[2]	= 493.67;
      combo_child_masses[3]	= 139.57;
     
      track_eff_const		= 1.00;
      track_eff_slope		= 0.00;
      
      beta_factor		= 0.01;
      
      trig_pt_cut_2body		= 1500.;
      trig_pt_cut_3body		= 750.;
      trig_ip_cut_2body		= 0.200;
      trig_ip_cut_3body		= 0.125;
      
      num_event_types		= 2;
      event_compositions[0]	= 0.90;
      event_compositions[1]	= 0.10;
      event_lifetime[0]		= b_lifetime;
      event_lifetime[1]		= combo_lifetime;
      event_names[0]            = "sig";
      event_names[1]		= "combo"; 
      event_color[0]		= 2;
      event_color[1]		= 3;
 
      examplefit_filename	= "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/ExampleToyFit.eps";
      pull_filename 		= "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/SwimmingToyPull_B2Dh.eps";

      // Plotting options
      model_prec		= 10000000;
      event_yield		= 0.;

      datafit_filename          = "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/DataFit.eps";

    }

    virtual ~ConfigParams(){}
};

#endif
