from Bio import SeqIO
from selenium import webdriver
import time
import re
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, NoSuchElementException
from multiprocessing import Process, Manager



# Reading Fasta file details in list
fileAddress = 'C:/Users/Tawfique/Downloads/Chlamydia Sequence.fasta'
chromeDriverPath='C:/Users/Tawfique/PycharmProjects/chromedriver.exe'
description = []
sequence = []
descriptionAndSequence = []
records=[]

for record in SeqIO.parse(fileAddress, "fasta"):
    description.append(record.description)
    sequence.append(str(record.seq))
    descriptionAndSequence.append(">"+record.description+""+str(record.seq))
    records.append(record.format("fasta"))


iteration_count=range(len(sequence))
pI=[]
Mw=[]
NLS=[]
Humploc = []
Bacello = []



def loop_Expasy(pI,Mw,iter):
    for e in iter:
        driverExpasy = webdriver.Chrome(chromeDriverPath)
        try:

        # Manipulating Expasy webpage

           driverExpasy.get("https://web.expasy.org/compute_pi/")

        # Putting the sequence value in the text box of Expasy
           driverExpasy.find_element_by_name("protein").send_keys(sequence[e])

    # Click the compute button Expasy

           driverExpasy.find_element_by_xpath('//*[@id="sib_body"]/form/p[4]/input[1]').click()

    # Extract the details from Expasy

           sequenceDetailsExpasy = driverExpasy.find_element_by_xpath('//*[@id="sib_body"]')
           sequenceDetailsExpasyText = sequenceDetailsExpasy.text
           pIMw = (str(sequenceDetailsExpasyText.splitlines()[(len(sequenceDetailsExpasyText.splitlines()) - 1)]))
           pIStr = re.search("(?<=:\s)(.*?)(?=\s\/)", pIMw)
           pI.append(pIStr.group())
           MwStr = re.search("(?<=\/\s)(.*?)(?=$)", pIMw)
           Mw.append(MwStr.group())

           driverExpasy.quit()
        except TimeoutException:
            pI.append(None)
            Mw.append(None)
            driverExpasy.quit()
            pass
        except NoSuchElementException:
            pI.append(None)
            Mw.append(None)
            driverExpasy.quit()
            pass
        print("Expasy"+str(e))
        time.sleep(5)


def loop_NLS(NLS,iter):
    for n in iter:
        driverNLS = webdriver.Chrome(chromeDriverPath)
        try:
        # Manipulating NLS webpage

           driverNLS.get("http://nls-mapper.iab.keio.ac.jp/cgi-bin/NLS_Mapper_form.cgi")

        # Select Cut off 2.0 NLS

           driverNLS.find_element_by_xpath('/html/body/form/ul[2]/li/h4/input[1]').click()

        # Select Entire region NLS

           driverNLS.find_element_by_xpath('/html/body/form/ul[3]/li/h4/input[2]').click()

        # Putting the sequence value in the text box of NLS

           driverNLS.find_element_by_name("typedseq").send_keys(sequence[n])

        # Predict NLS button click

           driverNLS.find_element_by_xpath('/html/body/form/h4/input[1]').click()

        # Extract max NLS value

           sequenceDetailsNls = driverNLS.find_element_by_xpath('/html/body/table[3]/tbody/tr[3]/td[3]')
           sequenceDetailsNlsText = sequenceDetailsNls.text
           if len(sequenceDetailsNlsText) == 0:
              NLS.append(0)
              driverNLS.quit()
           else:
              nlsMax = max([eval(nls) for nls in sequenceDetailsNlsText.splitlines()])
              NLS.append(nlsMax)
              driverNLS.quit()
        except TimeoutException:
            NLS.append(None)
            driverNLS.quit()
            pass
        except NoSuchElementException:
            NLS.append(None)
            driverNLS.quit()
            pass
        print("NLS" + str(n))
        time.sleep(5)


def loop_Humploc(Humploc,iter):
    for h in iter:
        # Manipulating Humploc website
        driver = webdriver.Chrome(chromeDriverPath)

        # Putting Fasta in text box Humploc
        try:
            driver.get("http://www.csbio.sjtu.edu.cn/bioinf/hum-multi-2/")
            driver.find_element_by_name("S1").send_keys(records[h])
            driver.find_element_by_xpath('/html/body/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/input[1]').click()
            alert = driver.switch_to.alert
            alert.accept()
            Humploc.append(None)
            driver.quit()
        except NoAlertPresentException:
            predictedLocationHumpLoc = driver.find_element_by_xpath('//*[@id="table1"]/tbody/tr[8]/td/table/tbody/tr[2]/td[2]/strong/font')
            predictedLocationHumpLocText = str(predictedLocationHumpLoc.text)
            Humploc.append(predictedLocationHumpLocText)
            driver.quit()

        except TimeoutException:
            Humploc.append(None)
            driver.quit()
            pass
        time.sleep(5)
        print('Humploc'+str(h))


def loop_Bacello(Bacello,iter):
    for b in iter:
        driverBacello = webdriver.Chrome(chromeDriverPath)
        try:
           driverBacello.get("http://gpcr.biocomp.unibo.it/bacello/pred.htm")

        # Select Animal Bacello

           driverBacello.find_element_by_xpath('//*[@id="content"]/form/p[1]/label[1]').click()

        # Putting Fasta in text box Bacello

           driverBacello.find_element_by_xpath('//*[@id="textarea"]').send_keys(records[b])

        # Click Submit button Bacello

           driverBacello.find_element_by_xpath('//*[@id="content"]/form/p[4]/input[1]').click()

        # Wait until page loads

           WebDriverWait(driverBacello, 600).until(EC.presence_of_element_located(('xpath', '//*[@id="content"]/table/tbody/tr[2]/td[2]')))

        # Extract predicted location Bacello

           predictedLocationBacello = driverBacello.find_element_by_xpath('//*[@id="content"]/table/tbody/tr[2]/td[2]')
           predictedLocationBacelloText = str(predictedLocationBacello.text)
           Bacello.append(predictedLocationBacelloText)
           driverBacello.quit()
        except TimeoutException:
            Bacello.append(None)
            driverBacello.quit()
            pass
        except NoSuchElementException:
            Bacello.append(None)
            driverBacello.quit()
            pass
        print('Bacello'+str(b))






if __name__ == '__main__':
# Managers to access server process for appending lists
    manager=Manager()
    pI=manager.list()
    Mw=manager.list()
    NLS=manager.list()
    Humploc=manager.list()
    Bacello=manager.list()
# Running the processes
    P1=Process(target=loop_Expasy,args=(pI,Mw,iteration_count))
    P2=Process(target=loop_NLS,args=(NLS,iteration_count))
    P3=Process(target=loop_Humploc,args=(Humploc,iteration_count))
    P4=Process(target=loop_Bacello,args=(Bacello,iteration_count))
    P1.start()
    P2.start()
    P3.start()
    P4.start()
    P1.join()
    P2.join()
    P3.join()
    P4.join()
    if all(len(x)==len(sequence) for x in [description,pI,Mw,NLS,Humploc,Bacello]):
# Write to csv after storing in a pandas dataframe for further manipulation
       dataFrameToExport = pd.DataFrame({'Description':description,'pI': list(pI), 'Mw': list(Mw), 'NLS': list(NLS), 'Humploc': list(Humploc), 'Bacello': list(Bacello)})
       dataFrameToExport.to_csv('C:/Users/Tawfique/Downloads/Chlamydia 434 Bu.csv')
    else:
        pass


