echo $1
echo $2

python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --mode all 
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --mode nonres
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --mode phipi
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --mode kstk
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --mode kpipi
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --mode pipipi

python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var CharmMass --mode all 
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var CharmMass --mode nonres
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var CharmMass --mode phipi
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var CharmMass --mode kstk
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var CharmMass --mode kpipi
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var CharmMass --mode pipipi

python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var BacPIDK --mode all
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var BacPIDK --mode nonres
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var BacPIDK --mode phipi
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var BacPIDK --mode kstk
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var BacPIDK --mode kpipi
python plotMDFitter.py $1 --configName $2 --pol both --year run1 --merge both --var BacPIDK --mode pipipi

  
