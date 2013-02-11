#include <iostream>
#include <fstream>
#include <TStyle.h>
#include <TCanvas.h>
#include <math.h>
#include <TH1.h>
#include <TH2.h>
#include <vector>
#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TGraph.h>
#include <TRandom3.h>
#include <TLorentzVector.h>
#include <TGenPhaseSpace.h>
#include <TVector3.h>
#include <string>
#include "TMatrixD.h"
#include <TMinuit.h>
#include <RooPoisson.h>
#include <ConfigParams.h>

using namespace std;

// ===================================================================================================================================
// End variable definition
// ===================================================================================================================================

class Candidate {
  public:

	Candidate(){}

	virtual ~Candidate(){}

	double 			getDecayTime_B(){return m_decayTime_B;}
	double 			getDecayTime_D(){return m_decayTime_D;}	
	double			getMeasuredMass(){return m_measuredMass;}
	TLorentzVector		getFourMomentum_B(){return m_fourMomentum_B;}
	TLorentzVector		getFourMomentum_D(){return m_fourMomentum_D;}	
	TGenPhaseSpace		getDecayParams_B(){return m_decayParams_B;}
        TGenPhaseSpace		getDecayParams_D(){return m_decayParams_D;}
	bool			getRecodInfo(int kid){return m_recod[kid];}
	std::vector<double>	getTP(){return m_tp;}

	int setTP(std::vector<double> tp){m_tp = tp; return 1;}
	int setDecayTime_B(double dt){m_decayTime_B = dt; return 1;}
	int setDecayTime_D(double dt){m_decayTime_D = dt; return 1;}	
	int setMeasuredMass(double mm){m_measuredMass=mm; return 1;}
	int setFourMomentum_B(TLorentzVector fmom){m_fourMomentum_B = fmom; return 1;}
	int setFourMomentum_D(TLorentzVector fmom){m_fourMomentum_D = fmom; return 1;}
	int setDecayParams_B(TGenPhaseSpace dpars){m_decayParams_B = dpars; return 1;}
	int setDecayParams_D(TGenPhaseSpace dpars){m_decayParams_D = dpars; return 1;}
	int setRecodInfo(int kid,bool recoed){m_recod[kid] = recoed;return 1;}
  private:
	double 			m_decayTime_B;
	double 			m_decayTime_D;	
	std::vector<double>	m_tp;
	double			m_measuredMass;
	TLorentzVector  	m_fourMomentum_B;
	TLorentzVector  	m_fourMomentum_D;	
	TGenPhaseSpace		m_decayParams_B;
        TGenPhaseSpace		m_decayParams_D;
	bool 			m_recod[4];
};
typedef std::pair<std::vector<TVector3>, Candidate> Event;
typedef std::vector<Event> 			    Events;
typedef std::pair<double,double>		    FitResult;

Events dataset 		= Events();
Events aftertrigger 	= Events();

ConfigParams fitconfig 	= ConfigParams();

// ===================================================================================================================================

double					Get3DIP(TVector3, TVector3, TVector3);

Candidate 				GenerateB(TH1F*,TH1F*,TH1F*,int,TRandom3*);
Event					GenerateEvent(TH1F*,TH1F*,TH1F*,TH1F*,TH1F*,TH1F*,int,TRandom3*);
bool					ApplyTrigger(Event);

std::vector<double>			            FindAccIntervals(Event);
std::vector<std::pair<double,bool> >	RefineTPs(Event, std::vector<std::pair<double,bool> >,double);

double 					GetLifetimeLikelihood(double, std::vector<double>, double);
void					fcn(Int_t&, Double_t*, Double_t&, Double_t*, Int_t);

int 					Generate_B2Dh(	int nevents, TRandom3* gR, 
							const char* tuplename = "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/SwimBu2DuPiTuple_Merged_1fb.root");
                                                    //"/Users/Gligorov/Work/CERN_Work/Selections/Stripping15/B2Dh/260711/MergedTree.root");
TCanvas* 				GenerateAndFit_B2Dh(	int nsamples, int nevents, ConfigParams config, int seed = 0,
							const char* tuplename = "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/SwimBu2DuPiTuple_Merged_1fb.root");
                                                    //"/Users/Gligorov/Work/CERN_Work/Selections/Stripping15/B2Dh/260711/MergedTree.root");

FitResult 				Fit_B2Dh();
int 					ReadDataFromNtuple( const char* tuplename = "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/SwimBu2DuPiTuple_Merged_1fb.root");
                                                    //"/Users/Gligorov/Work/CERN_Work/DsKWork/DsPiLifetimeData/SwimBu2DuPiTuple_Merged_1fb_ChildInfo.root");
TCanvas* 				ReadAndFit_B2Dh(const char* tuplename = "/afs/cern.ch/work/g/gligorov/public/SwimmingTuples/SwimBu2DuPiTuple_Merged_1fb.root");
                                                    //"/Users/Gligorov/Work/CERN_Work/DsKWork/DsPiLifetimeData/SwimBu2DuPiTuple_Merged_1fb_ChildInfo.root"); 

TH1F* 					PlotData(TCanvas* c, int nbins = 200, double low = 0., double high = 15.);
TH1F* 					PlotModel(TCanvas* c, FitResult outcome, int nbins = 200, double low = 0., double high = 15.);
TH1F*					PlotPull(TCanvas* c, TH1F* datahisto, TH1F* modelhisto, int nbins = 200, double low = 0., double high = 15.);

// ===================================================================================================================================

double GetLifetimeLikelihood(double tau_m, std::vector<double> tp_m, double tau){
	double TPSum = 0.;
	std::vector<double>::iterator firsttp = tp_m.begin();
	if (tp_m.size() == 1) {
		TPSum = exp(-1.*(*firsttp)/tau);
	} else {
		std::vector<double>::iterator  thistp = firsttp;
		double tp1 = *thistp;
		double tp2 = *(++thistp);
		TPSum += ( 	exp(-tp1/tau)*(1 - 					//regular term, no beta factor
						fitconfig.beta_factor*tau	- 	//first beta factor term
						fitconfig.beta_factor*tp1)		//second beta factor term
				-
				exp(-tp2/tau)*(1 - 					//regular term, no beta factor
						fitconfig.beta_factor*tau	- 	//first beta factor term
						fitconfig.beta_factor*tp2)		//second beta factor term
     			 );
		++thistp;
		while (thistp != tp_m.end()) {
			tp1 = *thistp;
			tp2 = *(++thistp);
			TPSum += ( 	exp(-tp1/tau)*(1 - 					//regular term, no beta factor
							fitconfig.beta_factor*tau	- 	//first beta factor term
							fitconfig.beta_factor*tp1)		//second beta factor term
					-
					exp(-tp2/tau)*(1 - 					//regular term, no beta factor
							fitconfig.beta_factor*tau	- 	//first beta factor term
							fitconfig.beta_factor*tp2)		//second beta factor term
     				 );
			++thistp; 
		}
	}
	if (TPSum < 0.) return 1.; //Protect against events with a crazy acceptance due to the beta function
	return (1./tau)*exp(-1.*tau_m/tau)*(1./TPSum);
}

void fcn(Int_t &npar, Double_t *gin, Double_t &f, Double_t *par, Int_t iflag) {

	double logL = 0.;

	for (Events::iterator ei = aftertrigger.begin(); ei != aftertrigger.end(); ++ei) {
		//cout << (*ei).second.getDecayTime_B() << endl;
		//cout << *((*ei).second.getTP().begin()) << endl;
		logL += log(	par[0]*GetLifetimeLikelihood(	(*ei).second.getDecayTime_B(),
										(*ei).second.getTP(),
										par[1]) +
				par[2]*GetLifetimeLikelihood(	(*ei).second.getDecayTime_B(),
										(*ei).second.getTP(),
										par[3]) 
			);
	}

	f =  -2*logL;
	
}
// ===================================================================================================================================

double Get3DIP(TVector3 direction, TVector3 decayvtx, TVector3 primvtx) {

        // Calculates the 3D impact parameters, whether online or offline.
        TVector3 r;
        r[0] = decayvtx[0] - direction[0]*(decayvtx[2] - primvtx[2])/direction[2] - primvtx[0]; //transport to PV position
        r[1] = decayvtx[1] - direction[1]*(decayvtx[2] - primvtx[2])/direction[2] - primvtx[1];
        r[2] = 0; 
        TVector3 IP = direction.Cross(r.Cross(direction)); //Standard stuff
        Double_t IPmag = IP.Mag();
        //if (IP[2] < 0) IPmag *= - 1; 
        return IPmag;

}

Candidate GenerateB(TH1F* bmomdistx,TH1F* bmomdisty,TH1F* bmomdistz, int bcat, TRandom3* gR) {	

	Candidate bCandidate = Candidate();

	if (bcat == 1) {

		double btau = gR->Exp(fitconfig.b_lifetime) + gR->Gaus(0,fitconfig.b_lifetime_res);
		bCandidate.setDecayTime_B(btau);
		double dtau = gR->Exp(fitconfig.d_lifetime) + gR->Gaus(0,fitconfig.b_lifetime_res);
		bCandidate.setDecayTime_D(dtau);
	
		double bmm = fitconfig.b_mass+gR->Gaus(0,fitconfig.b_mass_res);
		bCandidate.setMeasuredMass(bmm);
	
		double bpx = bmomdistx->GetRandom();
		double bpy = bmomdisty->GetRandom();
		double bpz = bmomdistz->GetRandom();
		double bpe = sqrt(pow(bmm,2)+pow(bpx,2)+pow(bpy,2)+pow(bpz,2));
		TLorentzVector thisb = TLorentzVector(bpx,bpy,bpz,bpe);
		bCandidate.setFourMomentum_B(thisb);
	
		TGenPhaseSpace bDecay = TGenPhaseSpace();
		bDecay.SetDecay(thisb,2,&(fitconfig.b_child_masses[0]));
		bDecay.Generate();
		bCandidate.setDecayParams_B(bDecay);
		TLorentzVector* thisd = bDecay.GetDecay(0);
		bCandidate.setFourMomentum_D(*thisd);	
	        TGenPhaseSpace dDecay = TGenPhaseSpace();
		dDecay.SetDecay(*thisd,fitconfig.numdkids,&(fitconfig.d_child_masses[0]));
		dDecay.Generate();
		bCandidate.setDecayParams_D(dDecay);
	
		for (int kid=0;kid<fitconfig.numdkids+1;++kid){
			bool recod = false;
			if (gR->Rndm() < (fitconfig.track_eff_const-fitconfig.track_eff_slope*btau)) recod = true;
			bCandidate.setRecodInfo(kid,recod);
		}
	} else if (bcat == 10) {
		double btau = gR->Exp(fitconfig.combo_lifetime) + gR->Gaus(0,fitconfig.b_lifetime_res);
		bCandidate.setDecayTime_B(btau);
		double dtau = gR->Exp(fitconfig.d_lifetime) + gR->Gaus(0,fitconfig.b_lifetime_res);
		bCandidate.setDecayTime_D(dtau);
	
		double bmm = fitconfig.combo_mass_low + gR->Rndm()*(fitconfig.combo_mass_high-fitconfig.combo_mass_low);
		bCandidate.setMeasuredMass(bmm);
	
		double bpx = bmomdistx->GetRandom();
		double bpy = bmomdisty->GetRandom();
		double bpz = bmomdistz->GetRandom();
		double bpe = sqrt(pow(bmm,2)+pow(bpx,2)+pow(bpy,2)+pow(bpz,2));
		TLorentzVector thisb = TLorentzVector(bpx,bpy,bpz,bpe);
		bCandidate.setFourMomentum_B(thisb);
	
		TGenPhaseSpace bDecay = TGenPhaseSpace();
		bDecay.SetDecay(thisb,2,&(fitconfig.b_child_masses[0]));
		bDecay.Generate();
		bCandidate.setDecayParams_B(bDecay);
		TLorentzVector* thisd = bDecay.GetDecay(0);
		bCandidate.setFourMomentum_D(*thisd);	
	        TGenPhaseSpace dDecay = TGenPhaseSpace();
		dDecay.SetDecay(*thisd,fitconfig.numdkids,&(fitconfig.d_child_masses[0]));
		dDecay.Generate();
		bCandidate.setDecayParams_D(dDecay);
	
		for (int kid=0;kid<fitconfig.numdkids+1;++kid){
			bool recod = false;
			if (gR->Rndm() < (fitconfig.track_eff_const-fitconfig.track_eff_slope*btau)) recod = true;
			bCandidate.setRecodInfo(kid,recod);
		}
	}

	return bCandidate;
}

Event	GenerateEvent(	TH1F* bmomdistx, TH1F* bmomdisty,TH1F* bmomdistz ,
			TH1F* pvxdist,	 TH1F* pvydist,	 TH1F* pvzdist, 
			int bcat, TRandom3* gR ) {
	int npv = gR->Poisson(fitconfig.mutogen);
	if (fitconfig.debug_mode) {cout << "Generated event with " << npv << " PVs" << endl;}
        if (npv == 0) npv += 1;
	std::vector<TVector3> primaryVertex; TVector3 onePV;
	for (int thisvert = 0; thisvert < npv; ++thisvert) {
		onePV	= TVector3(	pvxdist->GetRandom(),
					pvydist->GetRandom(),
					pvzdist->GetRandom());
		primaryVertex.push_back(onePV);
	}
	Candidate	bCandidate	= GenerateB(bmomdistx,bmomdisty,bmomdistz,bcat,gR);	
	Event 		eventToGenerate = Event(primaryVertex,bCandidate);

	return eventToGenerate;
}

bool	ApplyTrigger(Event candidateEvent) {
	
	TVector3 bPV = (*(candidateEvent.first.begin()));

	int child_passing_condition_twobody 	= 0;
	int child_passing_condition_threebody	= 0;

	TGenPhaseSpace bdecay 	= candidateEvent.second.getDecayParams_B();
        TGenPhaseSpace ddecay 	= candidateEvent.second.getDecayParams_D();
	TLorentzVector bmom	= candidateEvent.second.getFourMomentum_B();
        TLorentzVector dmom     = candidateEvent.second.getFourMomentum_D(); 
	double bpropertime	= candidateEvent.second.getDecayTime_B();
	double dpropertime	= candidateEvent.second.getDecayTime_D();	
	TVector3 decayvertex_B(	bPV.x()+bmom.Px()*0.3*bpropertime/bmom.M(),
				bPV.y()+bmom.Py()*0.3*bpropertime/bmom.M(),
				bPV.z()+bmom.Pz()*0.3*bpropertime/bmom.M());
        TVector3 decayvertex_D(	decayvertex_B.x()+dmom.Px()*0.3*dpropertime/dmom.M(),
				decayvertex_B.y()+dmom.Py()*0.3*dpropertime/dmom.M(),
				decayvertex_B.z()+dmom.Pz()*0.3*dpropertime/dmom.M());

	/*cout << PV.x() << " " << PV.y() << " " << PV.z() << endl;
	cout << bmom.Px() << " " << bmom.Py() << " " << bmom.Pz() << " " << bmom.M() << endl;
	cout << bpropertime << " " << decayvertex_B.x() << " " << decayvertex_B.y() << " " << decayvertex_B.z() << endl;
	cout << dpropertime << " " << decayvertex_D.x() << " " << decayvertex_D.y() << " " << decayvertex_D.z() << endl;*/

	TLorentzVector* thiskid;
	TVector3 thiskidmom;
	double thisIP, minIP;
	for (int kid=0;kid<fitconfig.numdkids;++kid){

		if (kid==0) {
			thiskid = bdecay.GetDecay(0);
			thiskidmom = TVector3(thiskid->Px(),thiskid->Py(),thiskid->Pz());
			minIP = 999999999.;
			for (std::vector<TVector3>::iterator thisPV = candidateEvent.first.begin(); 
				thisPV != candidateEvent.first.end(); ++thisPV) {
				thisIP = Get3DIP(thiskidmom.Unit(),decayvertex_B,*thisPV);
				if (thisIP < minIP) minIP = thisIP;
			}
		} else {
			thiskid = ddecay.GetDecay(kid-1);
			thiskidmom = TVector3(thiskid->Px(),thiskid->Py(),thiskid->Pz());
			minIP = 999999999.;			
			for (std::vector<TVector3>::iterator thisPV = candidateEvent.first.begin(); 
				thisPV != candidateEvent.first.end(); ++thisPV) {
				thisIP = Get3DIP(thiskidmom.Unit(),decayvertex_D,*thisPV);
				if (thisIP < minIP) minIP = thisIP;				
			}
		}

		//cout << thisIP << endl;

		if (!(candidateEvent.second.getRecodInfo(kid))) continue;

		//Category 1
		if (	thiskid->Pt() 	> fitconfig.trig_pt_cut_2body &&
			minIP		> fitconfig.trig_ip_cut_2body ) ++child_passing_condition_twobody;
		if (	thiskid->Pt() 	> fitconfig.trig_pt_cut_3body &&
			minIP		> fitconfig.trig_ip_cut_3body ) ++child_passing_condition_threebody;

	}

	
	if (child_passing_condition_twobody > 1 || child_passing_condition_threebody > 2) { 
		return true;
	} else return false;

	return true;
}

std::vector<std::pair<double,bool> > RefineTPs(Event eventforswimming, std::vector<std::pair<double,bool> > turning_points, double granularity) {
	std::vector<std::pair<double,bool> > turning_points_temp;

	Event swumevent = eventforswimming;
	turning_points_temp.push_back(*(turning_points.begin()));
	bool passed = (*(turning_points.begin())).second; bool lastpassed = passed;
	std::pair<double,bool> tpdata;
	for (std::vector<std::pair<double,bool> >::iterator thisTP = turning_points.begin() + 1; 
		thisTP != turning_points.end()-1; ++thisTP ) {
		for (double 	swimpoint = (*thisTP).first-granularity; 
				swimpoint < (*thisTP).first+granularity;
				swimpoint += granularity/fitconfig.swimratio) {

			swumevent.second.setDecayTime_B(swimpoint);
			passed = ApplyTrigger(swumevent);
			if (passed != lastpassed) {
				lastpassed = passed;
				tpdata.first = swimpoint; tpdata.second = passed;
				turning_points_temp.push_back(tpdata);
			}

		}
	}
	turning_points_temp.push_back(*(turning_points.end()-1));	

	return turning_points_temp;
}

std::vector<double> FindAccIntervals(Event eventforswimming) {

	std::vector<std::pair<double,bool> > turning_points;

	//Find rough TPs
	Event swumevent = eventforswimming;
	swumevent.second.setDecayTime_B(fitconfig.lowerswimrange);
	bool passed = ApplyTrigger(swumevent);
	std::pair<double,bool> tpdata; tpdata.first = fitconfig.lowerswimrange; tpdata.second = passed;
	turning_points.push_back(tpdata);

	bool lastpassed = passed;
	for (double 	swimpoint = fitconfig.lowerswimrange+fitconfig.swimgranularity; 
			swimpoint < fitconfig.upperswimrange; 
			swimpoint += fitconfig.swimgranularity) {
		swumevent.second.setDecayTime_B(swimpoint);
		passed = ApplyTrigger(swumevent);
		if (passed != lastpassed) {
			lastpassed = passed;
			tpdata.first = swimpoint; tpdata.second = passed;
			turning_points.push_back(tpdata);
		}
	}

	swumevent.second.setDecayTime_B(fitconfig.upperswimrange);
	passed = ApplyTrigger(swumevent);
	tpdata.first = fitconfig.upperswimrange; tpdata.second = passed;
	turning_points.push_back(tpdata);

	//Now refine each TP
	double thisswimgranularity = fitconfig.swimgranularity;
	for (int swimiter = 0; swimiter < fitconfig.swimiters; ++swimiter) {
		turning_points = RefineTPs(eventforswimming,turning_points,thisswimgranularity);
		thisswimgranularity /= fitconfig.swimratio;
	}

	std::vector<double> acceptintervals;
	std::vector<std::pair<double,bool> >::iterator thisfinaltp = turning_points.begin();
	lastpassed = false;
	if ((*thisfinaltp).second) {
		acceptintervals.push_back((*thisfinaltp).first);
		lastpassed = true;
	}
	while (thisfinaltp != turning_points.end()) {
		passed = (*thisfinaltp).second;
		if (passed != lastpassed) {
			lastpassed = passed;
			acceptintervals.push_back((*thisfinaltp).first);
		}
		++thisfinaltp;
	}
	if (passed) acceptintervals.push_back(fitconfig.upperswimrange);

	/*cout << "Printing out the TPs of an event" << endl;
	for (std::vector<std::pair<double,bool> >::iterator thisroughtp = turning_points.begin();
		thisroughtp != turning_points.end(); ++thisroughtp) {
		cout << (*thisroughtp).first << " " << (*thisroughtp).second << endl;
		
	}
	cout << "Finished printing out the TPs of an event" << endl;

	cout << "Printing out the acceptance intervals of an event" << endl;	
	for (std::vector<double>::iterator thisaccept = acceptintervals.begin();
		thisaccept != acceptintervals.end(); ++thisaccept) {
		cout << *thisaccept << endl;	
	}
	cout << "Finished printing out the acceptance intervals TPs of an event" << endl;*/	

	return acceptintervals;

}

int Generate_B2Dh(int nevents, TRandom3* gR, const char* tuplename) {

	TFile* bParamsFile = new TFile(tuplename,"OPEN");
	TTree* bParamsTree = (TTree*) bParamsFile->Get("DecayTree");

	float pvx,pvy,pvz;
	float bpx,bpy,bpz;

	TH1F* pvx_hist = new TH1F("pvx","pvx",10000,-1.,1.);
	TH1F* pvy_hist = new TH1F("pvy","pvy",10000,-1.,1.);
	TH1F* pvz_hist = new TH1F("pvz","pvz",10000,-200.,200.);

	TH1F* bpx_hist = new TH1F("bpx","bpx",10000,-20000,20000);
	TH1F* bpy_hist = new TH1F("bpy","bpy",10000,-20000,20000);
	TH1F* bpz_hist = new TH1F("bpz","bpz",10000,0,500000);

	bParamsTree->SetBranchStatus("*",0);
	bParamsTree->SetBranchStatus("PVX",1); bParamsTree->SetBranchStatus("PVY",1); bParamsTree->SetBranchStatus("PVZ",1);
	bParamsTree->SetBranchStatus("lab0_PX",1); bParamsTree->SetBranchStatus("lab0_PY",1); bParamsTree->SetBranchStatus("lab0_PZ",1);

	bParamsTree->SetBranchAddress("PVX",&pvx); bParamsTree->SetBranchAddress("PVY",&pvy); bParamsTree->SetBranchAddress("PVZ",&pvz);
	bParamsTree->SetBranchAddress("lab0_PX",&bpx); bParamsTree->SetBranchAddress("lab0_PY",&bpy); bParamsTree->SetBranchAddress("lab0_PZ",&bpz);

	int nentries_B = (int) bParamsTree->GetEntries();

	//Load the histograms
	for (int j=0;j < 50000;++j){
		bParamsTree->GetEntry(j);
		pvx_hist->Fill(pvx); pvy_hist->Fill(pvy); pvz_hist->Fill(pvz); 
		bpx_hist->Fill(bpx); bpy_hist->Fill(bpy); bpz_hist->Fill(bpz);
	}

	cout << "Read the histograms from the ntuple, about to generate the events" << endl;
	cout << "Generating with signal fraction " << fitconfig.event_compositions[0] << endl;

	//Generate the candidates
	for (int event_i=0; event_i < nevents*fitconfig.event_compositions[0]; ++event_i) {
		if (fitconfig.verbose_mode) {cout << "About to generate one signal event" << endl;}
		Event thisevent = GenerateEvent(bpx_hist,bpy_hist,bpz_hist,pvx_hist,pvy_hist,pvz_hist,1,gR);
		if (fitconfig.verbose_mode) {cout << "Generated one signal event" << endl;}
		dataset.push_back(thisevent);
		if (gR->Rndm() > (1-fitconfig.beta_factor*thisevent.second.getDecayTime_B())) {--event_i; continue;}
		if (ApplyTrigger(thisevent)) aftertrigger.push_back(thisevent); else --event_i;
	}
	for (int event_i=0; event_i < nevents*fitconfig.event_compositions[1]; ++event_i) {
		if (fitconfig.verbose_mode) {cout << "About to generate one background event" << endl;}
		Event thisevent = GenerateEvent(bpx_hist,bpy_hist,bpz_hist,pvx_hist,pvy_hist,pvz_hist,10,gR);
		if (fitconfig.verbose_mode) {cout << "Generated one background event" << endl;}
		dataset.push_back(thisevent);
		if (gR->Rndm() > (1-fitconfig.beta_factor*thisevent.second.getDecayTime_B())) {--event_i; continue;}		
		if (ApplyTrigger(thisevent)) aftertrigger.push_back(thisevent); else --event_i;
	}

	cout << "Generated " << dataset.size() <<  " events" << endl;

	cout << "Accepted "  << aftertrigger.size() <<  " events" << endl;

	cout << "Swimming the events" << endl;

	for (Events::iterator ei = aftertrigger.begin(); ei != aftertrigger.end(); ++ei) {
		((*ei).second).setTP(FindAccIntervals(*ei));
	}
	
	bParamsFile->Close();
	
	return 1;
}

FitResult Fit_B2Dh() {	
		
	cout << "About to fit the events back" << endl;

	TMinuit myMinuit(10);
	gMinuit->SetFCN(fcn);
	Double_t arglist[10];
        Int_t ierflg = 0;	

	arglist[0] = 3.; 
        myMinuit.mnexcm("SET PRINTOUT", arglist , 1, ierflg);
        arglist[0] = 1.; 
        myMinuit.mnexcm("SET ERR", arglist , 1, ierflg);

	for (int evttype =0; evttype < fitconfig.num_event_types; ++evttype) {
	  gMinuit->mnparm(2*evttype,fitconfig.event_names[evttype]+"_frac", fitconfig.event_compositions[evttype], 0, 0, 1, ierflg);
	  if (evttype == 0 ) {
  	    gMinuit->mnparm(2*evttype+1, fitconfig.event_names[evttype]+"_tau" , 0.6, 0.1, 0, 10, ierflg);
	  } else {
	    gMinuit->mnparm(2*evttype+1, fitconfig.event_names[evttype]+"_tau" , fitconfig.event_lifetime[evttype], 0, 0, 10, ierflg);
	  }
	}

	arglist[0] = 10000; arglist[1] = 1.e-5;	

	myMinuit.mnexcm("MIGRAD", arglist ,2,ierflg);
        myMinuit.mnexcm("HESSE", arglist ,0,ierflg);
	
	double tft,tfterr;
	myMinuit.GetParameter(1,tft,tfterr);

	FitResult toreturn;

	toreturn.first = tft; toreturn.second = tfterr;

	return toreturn;
}

TH1F* PlotPull(TCanvas* c, TH1F* datahisto, TH1F* modelhisto, int nbins, double low, double high) {
	c->cd(2);
	TH1F* pullhisto = new TH1F("pullhisto","pullhisto",nbins,low,high);
	pullhisto->GetXaxis()->SetTitle("B lifetime (ps)");
	pullhisto->GetYaxis()->SetTitle("(Data - Model) Pull");
    pullhisto->GetYaxis()->SetTitleFont(62);
    pullhisto->GetYaxis()->SetTitleOffset(0.5);
    pullhisto->Add(datahisto,1.);
	pullhisto->Add(modelhisto,-1.);
	for (int thisbin = 0; thisbin < nbins; ++thisbin) {
		double todivide = datahisto->GetBinError(thisbin);
		if (todivide < 1.) todivide = 1.;
		pullhisto->SetBinContent(thisbin,pullhisto->GetBinContent(thisbin)/todivide);
		pullhisto->SetBinError(thisbin,sqrt(pow(datahisto->GetBinError(thisbin),2) + 
						    pow(modelhisto->GetBinError(thisbin),2))/todivide);
	}
	pullhisto->Draw("EP");
	return pullhisto;
}

TH1F* PlotData(TCanvas* c, int nbins, double low, double high) {

	cout << "Preparing to plot the data" << endl;

	TH1F* datahisto = new TH1F("datahisto","datahisto",nbins, low, high);
	datahisto->Sumw2();
	datahisto->GetXaxis()->SetTitle("B lifetime (ps)");
	datahisto->GetYaxis()->SetTitle("Event Fraction");
    datahisto->GetYaxis()->SetTitleFont(62);
    datahisto->GetYaxis()->SetTitleOffset(0.5);
	datahisto->SetLineColor(1); datahisto->SetMarkerColor(1);

	for (Events::iterator ei = aftertrigger.begin(); ei != aftertrigger.end(); ++ei) {
		datahisto->Fill((*ei).second.getDecayTime_B());
	}	

	c->cd(1);
	datahisto->Draw("EP");

	return datahisto;

}

TH1F* PlotModel(TCanvas* c, FitResult outcome, int nbins, double low, double high) {

	TH1F* modelhisto[fitconfig.num_event_types];
	TH1F* betafactorhisto[fitconfig.num_event_types];
	TH1F* acceptancehisto[fitconfig.num_event_types];
	TH1F* normhisto[fitconfig.num_event_types];

	TRandom3* gR = new TRandom3();
	gR->SetSeed(0);
	c->cd(1);

	cout << "Preparing to plot the model" << endl;

	for (int evttype =0; evttype < fitconfig.num_event_types; ++evttype) {

		double lifetimetomodel = outcome.first;
		if (evttype > 0) lifetimetomodel = fitconfig.event_lifetime[evttype];

		modelhisto[evttype] = new TH1F(	"modelhisto"+fitconfig.event_names[evttype],
						"modelhisto"+fitconfig.event_names[evttype], nbins, low, high);
		modelhisto[evttype]->GetXaxis()->SetTitle("B lifetime (ps)");
		modelhisto[evttype]->GetYaxis()->SetTitle("Event Fraction");
		modelhisto[evttype]->SetLineColor(fitconfig.event_color[evttype]); modelhisto[evttype]->SetMarkerColor(fitconfig.event_color[evttype]);
	
		// Fill the model histogram	
		for (int i = 0; i < fitconfig.model_prec; ++i) {
			modelhisto[evttype]->Fill(gR->Exp(lifetimetomodel),1./((double)fitconfig.model_prec));
		}
	
		betafactorhisto[evttype] = new TH1F(	"betafactorhisto"+fitconfig.event_names[evttype],
							"betafactorhisto"+fitconfig.event_names[evttype], nbins, low, high);
		betafactorhisto[evttype]->GetXaxis()->SetTitle("B lifetime (ps)");
		betafactorhisto[evttype]->GetYaxis()->SetTitle("Event Fraction");
		betafactorhisto[evttype]->SetLineColor(fitconfig.event_color[evttype]); betafactorhisto[evttype]->SetMarkerColor(fitconfig.event_color[evttype]);

		cout << "Filled the model histogram for event type " << fitconfig.event_names[evttype] << endl;
	
		// Fill the betafactor histogram
		for (int i = 0; i < nbins; ++i) {
			double binmean = low + (i + 0.5)*(high-low)/((double) nbins);
			betafactorhisto[evttype]->Fill(binmean,1.-fitconfig.beta_factor*binmean);
		}
	
		cout << "Filled the beta factor histogram for event type " << fitconfig.event_names[evttype] << endl;		
	
		acceptancehisto[evttype] = new TH1F(	"acceptancehisto"+fitconfig.event_names[evttype],
							"acceptancehisto"+fitconfig.event_names[evttype], nbins, low, high);
		acceptancehisto[evttype]->GetXaxis()->SetTitle("B lifetime (ps)");
		acceptancehisto[evttype]->GetYaxis()->SetTitle("Event Fraction");
		acceptancehisto[evttype]->SetLineColor(fitconfig.event_color[evttype]); acceptancehisto[evttype]->SetMarkerColor(fitconfig.event_color[evttype]);

		cout << "Filled the acceptance histogram for event type " << fitconfig.event_names[evttype] << endl;		

		// Fill the acceptance histogram
		for (Events::iterator ei = aftertrigger.begin(); ei != aftertrigger.end(); ++ei) {
			if (fitconfig.debug_mode) cout << "Acceptance for one event" << endl;
			std::vector<double> tps = (*ei).second.getTP();
			double binwidth = (high-low)/((double) nbins);
	
			std::vector<double>::iterator  thistp = tps.begin();
			double TPNorm = 0.0;
			do {
				double tp1 = *thistp;
				double tp2 = *(++thistp);
				TPNorm += ( exp(-tp1/outcome.first) - exp(-tp2/outcome.first) );
				if (fitconfig.debug_mode) cout << tp1 << " " << tp2 << endl;
				++thistp; 
			} while (thistp != tps.end());
			thistp = tps.begin();
			do {
				double tp1 = *thistp;
				double tp2 = *(++thistp);
				int binno = 0; double extranorm = 1.; double timetofill;
				for (timetofill = tp1; timetofill < tp2; timetofill += binwidth) {
					if (binno == 0) extranorm = ceil(tp1/binwidth) - tp1/binwidth;
					else extranorm = 1.;
					acceptancehisto[evttype]->Fill(timetofill,extranorm/TPNorm);
					binno += 1;
				}
				timetofill = tp2;
				extranorm = tp2/binwidth - floor(tp2/binwidth);
				acceptancehisto[evttype]->Fill(timetofill,extranorm/TPNorm);
				++thistp; 
			} while (thistp != tps.end());
	
		}	
	
		modelhisto[evttype]->Multiply(betafactorhisto[evttype]); 
		modelhisto[evttype]->Multiply(acceptancehisto[evttype]);

		double integral = modelhisto[evttype]->Integral();
	
		normhisto[evttype] = new TH1F(	"normhisto"+fitconfig.event_names[evttype],
						"normhisto"+fitconfig.event_names[evttype], nbins, low, high);
		for (int i = 0; i < nbins; ++i) {
			double binmean = low + (i + 0.5)*(high-low)/((double) nbins);
			normhisto[evttype]->Fill(binmean,fitconfig.event_yield*fitconfig.event_compositions[evttype]/integral);
		}
		
		modelhisto[evttype]->Multiply(normhisto[evttype]);

		modelhisto[evttype]->Draw("SAME");

	}

	TH1F* totalmodelhisto = new TH1F("totalmodelhist","totalmodelhist",nbins,low,high);
	totalmodelhisto->GetXaxis()->SetTitle("B lifetime (ps)");
	totalmodelhisto->GetYaxis()->SetTitle("Event Fraction");
	totalmodelhisto->SetLineColor(4);  totalmodelhisto->SetMarkerColor(4); 
	totalmodelhisto->SetLineWidth(3.5); totalmodelhisto->SetLineStyle(2);

	for (int evttype =0; evttype < fitconfig.num_event_types; ++evttype) {
		totalmodelhisto->Add(modelhisto[evttype]);
	}
	totalmodelhisto->Draw("SAME");

	return totalmodelhisto;

}

TCanvas* GenerateAndFit_B2Dh(	int nsamples, int nevents, ConfigParams config, int seed , const char* tuplename) {
	TRandom3* gR = new TRandom3();
	gR->SetSeed(seed);

	fitconfig = config;

	TCanvas* fitcanvas = new TCanvas("fitcanvas","fitcanvas",1600,800);
	TH1F*	 fittau	   = new TH1F("fittau","fittau",100,fitconfig.b_lifetime-5*fitconfig.b_lifetime*sqrt((double) nevents)/((double) nevents),
                                                        fitconfig.b_lifetime+5*fitconfig.b_lifetime*sqrt((double) nevents)/((double) nevents));
	TH1F*	 fittauerr = new TH1F("fittauerr","fittauerr",100,  0.5*fitconfig.b_lifetime*sqrt((double) nevents)/((double) nevents),
                                                                1.5*fitconfig.b_lifetime*sqrt((double) nevents)/((double) nevents));
	TH1F*	 fitpull   = new TH1F("fitpull","fitpull",100,-5,5);

	FitResult result;
	for (int sample = 0; sample < nsamples; ++sample) {

		dataset 	= Events();
		aftertrigger	= Events();

		Generate_B2Dh(nevents,gR,tuplename);
		
		cout << "About to fit the events back" << endl;

		result = Fit_B2Dh();
		fitconfig.event_yield = nevents;

		fittau->Fill(result.first);
		fittauerr->Fill(result.second);
		fitpull->Fill((result.first-fitconfig.b_lifetime)/result.second);

	}

	TCanvas* toycanv = new TCanvas("toycanv","toycanv",1200,800);
	toycanv->Divide(1,2);
	toycanv->cd(1);
	TH1F* datahisto  = PlotData(toycanv);
	TH1F* modelhisto = PlotModel(toycanv,result);
	toycanv->GetPad(1)->SetLogy();
	toycanv->cd(2);
	TH1F* pullhisto  = PlotPull(toycanv,datahisto,modelhisto);

	toycanv->SaveAs(fitconfig.examplefit_filename);

	fitcanvas->Divide(3,1);
	fitcanvas->cd(1);
	fittau->Fit("gaus");
	fittau->Draw("EP");
	fitcanvas->cd(2);
	fittauerr->Fit("gaus");
	fittauerr->Draw("EP");
	fitcanvas->cd(3);
	fitpull->Fit("gaus");
	fitpull->Draw("EP");	

	fitcanvas->SaveAs(fitconfig.pull_filename);

	return fitcanvas;
}

int ReadDataFromNtuple( const char* tuplename) {

	TFile* bParamsFile = new TFile(tuplename,"OPEN");
	TTree* bParamsTree = (TTree*) bParamsFile->Get("DecayTree");

	int npv;
	float pvx[10];
	float pvy[10];
	float pvz[10];
	float mass;	
	float tau,taud,fdchi2;
	float bpx,bpy,bpz;

	int ntp_trig;
	int ntp_strip;

	float tp_trig_tau[100];
	float tp_strip_tau[100];	
	float tp_trig_dec[100];
	float tp_strip_dec[100];	

	TH1F* pvx_hist = new TH1F("pvx","pvx",10000,-1.,1.);
	TH1F* pvy_hist = new TH1F("pvy","pvy",10000,-1.,1.);
	TH1F* pvz_hist = new TH1F("pvz","pvz",10000,-200.,200.);

	TH1F* bpx_hist = new TH1F("bpx","bpx",10000,-20000,20000);
	TH1F* bpy_hist = new TH1F("bpy","bpy",10000,-20000,20000);
	TH1F* bpz_hist = new TH1F("bpz","bpz",10000,0,500000);

	bParamsTree->SetBranchStatus("*",0);
	bParamsTree->SetBranchStatus("PVX",1); bParamsTree->SetBranchStatus("PVY",1); bParamsTree->SetBranchStatus("PVZ",1); bParamsTree->SetBranchStatus("nPV",1);
	bParamsTree->SetBranchStatus("lab0_PX",1); bParamsTree->SetBranchStatus("lab0_PY",1); bParamsTree->SetBranchStatus("lab0_PZ",1);	
	bParamsTree->SetBranchStatus("lab0_MassFitConsD_M",1); bParamsTree->SetBranchStatus("lab0_TAU",1);
	bParamsTree->SetBranchStatus("lab0_Stripping_nTP",1); bParamsTree->SetBranchStatus("lab0_Trigger_nTP",1);
	bParamsTree->SetBranchStatus("lab0_Stripping_TP_DEC",1); bParamsTree->SetBranchStatus("lab0_Stripping_TP_TAU",1);
	bParamsTree->SetBranchStatus("lab0_Trigger_TP_DEC",1); bParamsTree->SetBranchStatus("lab0_Trigger_TP_TAU",1);	
	bParamsTree->SetBranchStatus("lab2_TAU",1); bParamsTree->SetBranchStatus("lab2_FDCHI2_ORIVX",1);

	bParamsTree->SetBranchAddress("PVX",&pvx); bParamsTree->SetBranchAddress("PVY",&pvy); bParamsTree->SetBranchAddress("PVZ",&pvz); bParamsTree->SetBranchAddress("nPV",&npv);
	bParamsTree->SetBranchAddress("lab0_PX",&bpx); bParamsTree->SetBranchAddress("lab0_PY",&bpy); bParamsTree->SetBranchAddress("lab0_PZ",&bpz);	
	bParamsTree->SetBranchAddress("lab0_MassFitConsD_M",&mass); bParamsTree->SetBranchAddress("lab0_TAU",&tau);
	bParamsTree->SetBranchAddress("lab0_Stripping_nTP",&ntp_strip); bParamsTree->SetBranchAddress("lab0_Trigger_nTP",&ntp_trig);	
	bParamsTree->SetBranchAddress("lab0_Stripping_TP_DEC",&tp_strip_dec); bParamsTree->SetBranchAddress("lab0_Stripping_TP_TAU",&tp_strip_tau);
	bParamsTree->SetBranchAddress("lab0_Trigger_TP_DEC",&tp_trig_dec); bParamsTree->SetBranchAddress("lab0_Trigger_TP_TAU",&tp_trig_tau);	
	bParamsTree->SetBranchAddress("lab2_TAU",&taud); bParamsTree->SetBranchAddress("lab2_FDCHI2_ORIVX",&fdchi2);	

	cout << "Set up the ntuple for reading" << endl;

	int nentries_B = (int) bParamsTree->GetEntries();

	//Load the histograms
	for (int j=0;j < 50000;++j){
		bParamsTree->GetEntry(j);
		pvx_hist->Fill(pvx[0]); pvy_hist->Fill(pvy[0]); pvz_hist->Fill(pvz[0]); 
		bpx_hist->Fill(bpx); bpy_hist->Fill(bpy); bpz_hist->Fill(bpz);
	}

	cout << "Read the histograms from the ntuple, about to generate the fake events" << endl;

	//Generate the candidates
	TRandom3* gR = new TRandom3();
	gR->SetSeed(0);
	for (int event_i=0; event_i < nentries_B; ++event_i) {
		Event thisevent = GenerateEvent(bpx_hist,bpy_hist,bpz_hist,pvx_hist,pvy_hist,pvz_hist,1,gR);
		dataset.push_back(thisevent);
	}

	//Load the histograms
	Events::iterator oneevent = dataset.begin(); int badevent = 0;
	for (int j=0;j < nentries_B;++j){
		bParamsTree->GetEntry(j);

		//cout << "Read event " << j << endl;

		if (!(mass > 5240. && mass < 5320.) || taud < 0. || fdchi2 < 4.) continue;

		if (fitconfig.debug_mode) {
			cout << "Event " << j << " with " << npv << " PVs passed the mass cut" << endl;		
			cout << "Added the PVs now adding lifetime " << tau << " and mass " << mass << endl;
		}

		(*oneevent).second.setMeasuredMass(mass);
		(*oneevent).second.setDecayTime_B(tau*1000.);

		std::vector<std::pair<double,bool> > turning_points_trig;
		std::vector<std::pair<double,bool> > turning_points_strip;
		std::pair<double,bool> tpdata;

		bool lastdec,thisdec,otherdec;
		tpdata.first = tp_trig_tau[0];
		tpdata.second = lastdec = tp_trig_dec[0];
		turning_points_trig.push_back(tpdata);

		for (int tptrig = 1; tptrig < ntp_trig; ++tptrig) { 
			if (tp_trig_tau[tptrig] < 0) {
				if (lastdec) {
					tpdata.first = 0.0;
					tpdata.second = true;
					turning_points_trig.push_back(tpdata);
				}
				break;
			}
			tpdata.first = tp_trig_tau[tptrig];
			tpdata.second = thisdec = tp_trig_dec[tptrig];
			if (thisdec!=lastdec) {
				turning_points_trig.push_back(tpdata);
				lastdec = thisdec;
			}
		}

		tpdata.first = tp_strip_tau[0];
		tpdata.second = lastdec = tp_strip_dec[0];
		turning_points_strip.push_back(tpdata);

		for (int tpstrip = 1; tpstrip < ntp_strip; ++tpstrip) { 
			if (tp_strip_tau[tpstrip] < 0) {
				if (lastdec) {
					tpdata.first = 0.0;
					tpdata.second = true;
					turning_points_strip.push_back(tpdata);
				}
				break;			
			}
			tpdata.first = tp_strip_tau[tpstrip];
			tpdata.second = thisdec = tp_strip_dec[tpstrip];
			if (thisdec != lastdec) {
				turning_points_strip.push_back(tpdata);
				lastdec = thisdec;
			}
		}

		// Merge the TPs and decisions
		std::vector<std::pair<double,bool> > turning_points_combined;
		std::vector<std::pair<double,bool> >::iterator tpiter_trig;
		std::vector<std::pair<double,bool> >::iterator tpiter_strip;
		std::vector<std::pair<double,bool> >::iterator tpiter_combined;		
		
		tpiter_trig = turning_points_trig.begin();
		tpiter_strip = turning_points_strip.begin();

		lastdec = (*tpiter_trig).second * (*tpiter_strip).second;
		tpdata.first = (*tpiter_trig).first; tpdata.second = lastdec;
		turning_points_combined.push_back(tpdata);

		++tpiter_strip; ++tpiter_trig;
				
		while( tpiter_trig != turning_points_trig.end() && tpiter_strip != turning_points_strip.end() ) {

			double thislifetime = (*tpiter_trig).first > (*tpiter_strip).first ? (*tpiter_trig).first : (*tpiter_strip).first;
			thisdec = (*tpiter_trig).first > (*tpiter_strip).first ? (*tpiter_trig).second : (*tpiter_strip).second;

			otherdec = (*tpiter_trig).first > (*tpiter_strip).first ? !(*tpiter_strip).second : !(*tpiter_trig).second;

			tpdata.first = thislifetime; tpdata.second = thisdec*otherdec; turning_points_combined.push_back(tpdata);

			(*tpiter_trig).first > (*tpiter_strip).first ? ++tpiter_trig : ++tpiter_strip;

		}

		tpiter_trig = turning_points_trig.begin();
		tpiter_strip = turning_points_strip.begin();
		tpiter_combined = turning_points_combined.begin();


		if (fitconfig.debug_mode) {
			cout << "These were the trigger turning points" << endl;
			while (tpiter_trig != turning_points_trig.end() ) {
				cout << (*tpiter_trig).first << " " << (*tpiter_trig).second << endl;
				++tpiter_trig;
			}

			cout << "These were the stripping turning points" << endl;

			while (tpiter_strip != turning_points_strip.end() ) {
				cout << (*tpiter_strip).first << " " << (*tpiter_strip).second << endl;
				++tpiter_strip;
			}

			cout << "These are the combined turning points" << endl;

			while (tpiter_combined != turning_points_combined.end() ) {
				cout << (*tpiter_combined).first << " " << (*tpiter_combined).second << endl;
				++tpiter_combined;
			}
		}

		//Now make the accept interval
		std::vector<double> acceptinterval_combined;
		tpiter_combined = turning_points_combined.begin();
		lastdec = false;

		if ((*tpiter_combined).second) {
			acceptinterval_combined.insert(acceptinterval_combined.begin(),1000.*(*tpiter_combined).first);
			lastdec = true;
		}
		while (tpiter_combined != turning_points_combined.end()) {
			thisdec = (*tpiter_combined).second;
			if (thisdec != lastdec) {
				lastdec = thisdec;
				acceptinterval_combined.insert(acceptinterval_combined.begin(),1000.*(*tpiter_combined).first);
			}
			++tpiter_combined;
		}

		if (fitconfig.debug_mode) {
			cout << "These are the acceptance intervals" << endl;
			std::vector<double>::iterator acceptintervaliter_combined = acceptinterval_combined.begin();
			while (acceptintervaliter_combined != acceptinterval_combined.end() ) {
				cout << (*acceptintervaliter_combined) << endl;
				++acceptintervaliter_combined;
			}
		}

		(*oneevent).second.setTP(acceptinterval_combined);

		if (acceptinterval_combined.size() == 0) {
			++badevent;
			continue;
		}

		aftertrigger.push_back(*oneevent);
	
		if (fitconfig.debug_mode) {
			cout << "About to push back the event" << endl;
		}

		++oneevent;
	}

	cout << "Threw away " << badevent << " bad events!!!!!" << endl;

	return 1;

}

TCanvas* ReadAndFit_B2Dh(const char* tuplename) {

	ReadDataFromNtuple(tuplename);
	
	FitResult result;

	result = Fit_B2Dh();

	TCanvas* datacanv = new TCanvas("datacanv","datacanv",1200,800);
	PlotData(datacanv);
	PlotModel(datacanv,result);

	datacanv->SetLogy();

	return datacanv;
}
