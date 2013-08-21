{
TChain* c = new TChain("DecayTree");
c->Add("/afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/DV_v33r1/SmallTuples/DsK_KKPi_PhiPi_M*");
c->Add("/afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/DV_v33r1/SmallTuples/DsK_KKPi_KstK_M*");
c->Add("/afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/DV_v33r1/SmallTuples/DsK_KKPi_NonRes_M*");
c->Add("/afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/DV_v33r1/SmallTuples/DsK_KPiPi_M*");
c->Add("/afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/DV_v33r1/SmallTuples/DsK_PiPiPi_M*");

TH1F* bin1 = new TH1F("bin1","bin1",20,1.6,5);
bin1->SetLineColor(1);
bin1->SetMarkerColor(1);
bin1->SetMarkerStyle(20);
bin1->SetLineStyle(1);
bin1->GetXaxis()->SetTitle("log(PIDK) of bachelor track");
bin1->GetYaxis()->SetTitle("Entries/0.17");

TH1F* bin2 = new TH1F("bin2","bin2",20,1.6,5);
bin2->SetLineColor(2);
bin2->SetMarkerColor(2);
bin2->SetMarkerStyle(21);
bin2->SetLineStyle(1);

TH1F* bin3 = new TH1F("bin3","bin3",20,1.6,5);
bin3->SetLineColor(3);
bin3->SetMarkerColor(3);
bin3->SetMarkerStyle(22);
bin3->SetLineStyle(1);

TH1F* bin4 = new TH1F("bin4","bin4",20,1.6,5);
bin4->SetLineColor(4);
bin4->SetMarkerColor(4);
bin4->SetMarkerStyle(23);
bin4->SetLineStyle(1);

TH1F* bin5 = new TH1F("bin5","bin5",20,1.6,5);
bin5->SetLineColor(6);
bin5->SetMarkerColor(6);
bin5->SetMarkerStyle(24);
bin5->SetLineStyle(1);

bin1->Sumw2();
bin2->Sumw2();
bin3->Sumw2();
bin4->Sumw2();
bin5->Sumw2();

c->Draw("log(lab1_PIDK)>>bin1","lab0_MassFitConsD_M[0]>5625. && lab0_MassFitConsD_M[0] < 5775. && lab1_PIDK > 5 && BDTGResponse_1 > 0.3 && lab2_MM > 1930 && lab2_MM < 2015");
c->Draw("log(lab1_PIDK)>>bin2","lab0_MassFitConsD_M[0]>5775. && lab0_MassFitConsD_M[0] < 5950. && lab1_PIDK > 5 && BDTGResponse_1 > 0.3 && lab2_MM > 1930 && lab2_MM < 2015");
c->Draw("log(lab1_PIDK)>>bin3","lab0_MassFitConsD_M[0]>5950. && lab0_MassFitConsD_M[0] < 6200. && lab1_PIDK > 5 && BDTGResponse_1 > 0.3 & lab2_MM > 1930 && lab2_MM < 2015");
c->Draw("log(lab1_PIDK)>>bin4","lab0_MassFitConsD_M[0]>6200. && lab0_MassFitConsD_M[0] < 6500. && lab1_PIDK > 5 && BDTGResponse_1 > 0.3 && lab2_MM> 1930 && lab2_MM < 2015");
c->Draw("log(lab1_PIDK)>>bin5","lab0_MassFitConsD_M[0]>6500. && lab0_MassFitConsD_M[0] < 7000. && lab1_PIDK > 5 && BDTGResponse_1 > 0.3 && lab2_MM> 1930 && lab2_MM < 2015");

TCanvas* canv = new TCanvas("canv","canv",800,600);
canv->cd(1);

bin1->DrawNormalized("EP");
bin1->GetYaxis()->SetRangeUser(0,0.125);
canv->Update();
bin2->DrawNormalized("SAME");
bin3->DrawNormalized("SAME");
bin4->DrawNormalized("SAME");
bin5->DrawNormalized("SAME");

TLegend* leg=new TLegend(0.65,0.65,0.925,0.925);
leg->SetFillStyle(0);
leg->SetMargin(0.25);
leg->SetTextSize(0.03);
leg->SetFillColor(0);
leg->AddEntry(bin1,"6500-7000 MeV", "lp");
leg->AddEntry(bin2,"6200-6500 MeV", "lp");
leg->AddEntry(bin3,"5950-6200 MeV", "lp");
leg->AddEntry(bin4,"5775-5950 MeV", "lp");
leg->AddEntry(bin5,"5625-5775 MeV", "lp");
leg->Draw("same");

canv->Update();

canv->SaveAs("PIDKInBSidebands.pdf");
canv->SaveAs("PIDKInBSidebands.png");
canv->SaveAs("PIDKInBSidebands.eps");
canv->SaveAs("PIDKInBSidebands.root");

}
