import threading
import time
from collections import deque
import collections
import os


# FIFO, Shortest Process Next Priority Scheduling, Round Robin
# CPU utilization, throughput, turnaround time, waiting time, response time


def parseTask():
    """
    This function will parse the txt file and assign the task to a dict
    :return: Task -> dict
    """
    with open("sample.txt") as file:
        raw_Task_Info = file.readlines()

    file.close()

    taskArray = deque([])
    for task in raw_Task_Info:
        task_info = task.split(" ")
        if task_info[0] == "proc":
            task_info[-1] = task_info[-1][0:-1]
            # proc : priority , [runtime] , [ wait time]
            procDict = [task_info[1]]
            runTime = deque([])
            waitTime = deque([])

            counter = 0
            for item in task_info[2:]:
                counter += 1
                # if counter is single it's execution time, else it's IO wait time
                if counter % 2 != 0:
                    runTime.append(item)
                else:
                    waitTime.append(item)
            procDict.append(runTime)
            procDict.append(waitTime)

            taskArray.append(procDict)

        if task_info[0] == "sleep":
            taskArray.append(["sleep", task_info[1][:-1]])

        if task_info[0] == "stop":
            taskArray.append(["stop"])
            return taskArray


def timeCounter(startTime, endTime):
    return (endTime - startTime) * 1000


def IOwait(readyQueue, IOQueue, totalRunningTime, totalWaitTime):
    """

    :param totalRunningTime:
    :param IOQueue:
    :param totalWaitTime:
    :param readyQueue: ready queue
    :return: total Wait time and total RunningTime
    """
    waitStartTime = time.time()
    if IOQueue:
        waitTime = IOQueue.popleft()
        time.sleep(float(waitTime) / 1000)
        waitEndTime = time.time()
        curWaitTime = timeCounter(waitStartTime, waitEndTime)
        totalWaitTime.append(curWaitTime)
        if readyQueue:
            CPUScheduler(readyQueue, IOQueue, totalRunningTime, totalWaitTime)
        if not readyQueue:
            return [totalRunningTime, totalWaitTime]


def CPUScheduler(readyQueue, IOQueue, totalRunningTime, totalWaitTime):
    """

    :param totalWaitTime:
    :param totalRunningTime:
    :param IOQueue:
    :param readyQueue:
    :return:
    """
    processStartTime = time.time()
    if readyQueue:
        executeTime = readyQueue.popleft()
        time.sleep(float(executeTime) / 1000)
        processEndTime = time.time()
        curRunningTime = timeCounter(processStartTime, processEndTime)
        totalRunningTime.append(curRunningTime)
        if IOQueue:
            IOwait(readyQueue, IOQueue, totalRunningTime, totalWaitTime)
        if not IOQueue:
            return [totalRunningTime, totalWaitTime]


# FCFS
def FCFS():
    """
    :return: CPU utilization, throughput, turnaround time, waiting time, response time
    """

    allTasks = parseTask()

    taskCount = 0
    AllTaskStartTime = time.time()

    totalRunningTimeList = []
    totalWaitingTimeList = []
    totalProcessTimeList = []
    totalResponseTimeList = []
    AllTaskRunningTime = 0

    while allTasks:
        curTask = allTasks.popleft()
        if curTask[0] == "sleep":
            taskCount += 1
            timeToSleep = float(curTask[1]) / 1000
            time.sleep(timeToSleep)
        elif curTask[0] != "stop":
            taskCount += 1
            readyQueue = curTask[1]
            IOQueue = curTask[2]

            turnAroundStartTime = time.time()

            while readyQueue or IOQueue:
                responseStartTime = time.time()
                processTime = CPUScheduler(readyQueue, IOQueue, [], [])
                responseEndTime = time.time()
                curResponseTime = timeCounter(responseStartTime, responseEndTime)
                totalResponseTimeList.append(curResponseTime)
                totalRunningTimeList.append(sum(processTime[0]))
                totalWaitingTimeList.append(sum(processTime[1]))

            turnAroundEndTime = time.time()
            curTurnAroundTime = timeCounter(turnAroundStartTime, turnAroundEndTime)
            totalProcessTimeList.append(curTurnAroundTime)

        else:
            AllTaskEndTime = time.time()
            AllTaskRunningTime += timeCounter(AllTaskStartTime, AllTaskEndTime)

            totalRunningTime = sum(totalRunningTimeList)
            totalWaitingTime = sum(totalWaitingTimeList)
            totalProcessTime = sum(totalProcessTimeList)
            totalResponseTime = sum(totalResponseTimeList)

            # cpu utilization =  execution time / total time
            # turnaround time =  ready stage -> completion time
            # wait time = total time - execution time
            # response time = process send in and out time
            # throughput = number of process completed per unit of time(100)

            cpu_Utilization = totalRunningTime / AllTaskRunningTime
            turnAroundTime = totalResponseTime
            waitTime = totalWaitingTime
            responseTime = totalProcessTime
            throughPut = AllTaskRunningTime / taskCount

            return [cpu_Utilization, turnAroundTime, waitTime, responseTime, throughPut]


# Shortest Process Next Priority Scheduling

def SPN():
    """
    :return: CPU utilization, throughput, turnaround time, waiting time, response time
    """

    allTasks = parseTask()
    allTaskStartTime = time.time()
    runningTimeReferenceTable = {}

    for task in allTasks:
        executionOrder = {}

        # get all the running time
        if task[0] != "stop":

            if task[0] != "sleep":
                totalRunningTime = 0
                for runningTime in task[1]:
                    totalRunningTime += int(runningTime)

                for waitingTime in task[2]:
                    totalRunningTime += int(waitingTime)
                runningTimeReferenceTable[totalRunningTime] = task

            else:
                totalRunningTime = int(task[1])
                runningTimeReferenceTable[totalRunningTime] = task
        else:
            break

    # sort task priority by time
    sortedTasksArray = collections.OrderedDict(sorted(runningTimeReferenceTable.items()))

    totalRunningTimeList = []
    totalWaitingTimeList = []
    totalProcessTimeList = []
    totalResponseTimeList = []

    taskCount = len(sortedTasksArray.keys())

    for taskReference in sortedTasksArray:
        currentTask = sortedTasksArray[taskReference]

        turnAroundStartTime = time.time()
        processStartTime = time.time()
        if currentTask[0] == "sleep":
            timeToSleep = float(currentTask[1]) / 1000
            time.sleep(timeToSleep)
        else:
            readyQueue = currentTask[1]
            IOQueue = currentTask[2]
            responseStartTime = time.time()
            results = CPUScheduler(readyQueue, IOQueue, [], [])
            processEndTime = time.time()
            processTime = timeCounter(responseStartTime, processEndTime)
            totalProcessTimeList.append(processTime)
            totalRunningTimeList.append(sum(results[0]))
            totalWaitingTimeList.append(sum(results[1]))

        turnAroundEndTime = time.time()
        turnAroundTime = timeCounter(turnAroundStartTime, turnAroundEndTime)
        totalResponseTimeList.append(turnAroundTime)

    allTaskEndTime = time.time()
    allTaskRunningTime = timeCounter(allTaskStartTime, allTaskEndTime)

    totalRunningTime = sum(totalRunningTimeList)
    totalWaitingTime = sum(totalWaitingTimeList)
    totalProcessTime = sum(totalProcessTimeList)
    totalResponseTime = sum(totalResponseTimeList)

    cpu_Utilization = totalRunningTime / allTaskRunningTime
    turnAroundTime = totalResponseTime
    waitTime = totalWaitingTime
    responseTime = totalProcessTime
    throughPut = allTaskRunningTime / taskCount

    return [cpu_Utilization, turnAroundTime, waitTime, responseTime, throughPut]


def PRI():
    """
    :return: CPU utilization, throughput, turnaround time, waiting time, response time
    """

    # because sleep have no priority, I choose to assign sleep into another scheduling list execute post all tasks(lowest priority)
    allTasks = parseTask()

    allTaskStartTime = time.time()
    allTasksReferenceTable = {}
    sleepList = []

    # categorize task
    for task in allTasks:
        if task[0] == "sleep":
            sleepList.append(int(task[1]))

        elif task[0] != "stop":
            priority = task[0]
            if priority not in allTasksReferenceTable:
                allTasksReferenceTable[priority] = [task]
            else:
                allTasksReferenceTable[priority].append(task)
        else:
            break

    taskCount = len(allTasksReferenceTable.keys())

    # sort task priority
    sortedTasksArray = collections.OrderedDict(sorted(allTasksReferenceTable.items()))

    totalRunningTimeList = []
    totalWaitingTimeList = []
    totalProcessTimeList = []
    totalResponseTimeList = []

    for taskID in allTasksReferenceTable:
        for currentTask in allTasksReferenceTable[taskID]:
            readyQueue = currentTask[1]
            IOQueue = currentTask[2]
            responseStartTime = time.time()
            results = CPUScheduler(readyQueue, IOQueue, [], [])
            processEndTime = time.time()
            processTime = timeCounter(responseStartTime, processEndTime)
            totalProcessTimeList.append(processTime)
            totalRunningTimeList.append(sum(results[0]))
            totalWaitingTimeList.append(sum(results[1]))

    for sleepTime in sleepList:
        time.sleep(sleepTime / 1000)

    allTaskEndTime = time.time()
    allTaskRunningTime = timeCounter(allTaskStartTime, allTaskEndTime)

    totalRunningTime = sum(totalRunningTimeList)
    totalWaitingTime = sum(totalWaitingTimeList)
    totalProcessTime = sum(totalProcessTimeList)
    totalResponseTime = sum(totalResponseTimeList)

    cpu_Utilization = totalRunningTime / allTaskRunningTime
    turnAroundTime = totalResponseTime
    waitTime = totalWaitingTime
    responseTime = totalProcessTime
    throughPut = allTaskRunningTime / taskCount

    return [cpu_Utilization, turnAroundTime, waitTime, responseTime, throughPut]


def menu():
    fileName = str(input("Input File Name: "))

    while True:
        if os.path.exists(fileName + ".txt"):
            print("CPU Scheduling Alg : FCFS|SPN|PRI")
            print("Enter FCFS for FCFS algorithm")
            print("Enter SPN for SPN algorithm")
            print("Enter PRI for PRI algorithm")
            selectedAlgorithm = str(input("Enter your algorithm of picking: "))
            while selectedAlgorithm not in ["FCFS", "SPN", "PRI"]:
                print("NOT VALID, PICK AGAIN")
                selectedAlgorithm = str(input("Enter your algorithm of picking: "))
            else:
                if selectedAlgorithm == "FCFS":
                    FIFOResult = FCFS()
                    print("Analysis for FIFO: ")
                    print("CPU utilization: " + str(round(FIFOResult[0] * 100, 2)) + "%")
                    print("Total Turn Around Time: " + str(round(FIFOResult[1], 2)) + "ms")
                    print("Total Wait Time: " + str(round(FIFOResult[2], 2)) + "ms")
                    print("Response Time: " + str(round(FIFOResult[3], 2)) + "ms")
                    print("ThroughPut: " + str(round(FIFOResult[4], 2)) + " per process")

                    option = input("continue? Y/N")
                    if option in ["N","n"]:
                        quit()
                    else:
                        option = ""
                        continue

                elif selectedAlgorithm == "SPN":
                    SPNResult = SPN()
                    print("Analysis for SPN: ")
                    print("CPU utilization: " + str(round(SPNResult[0] * 100, 2)) + "%")
                    print("Total Turn Around Time: " + str(round(SPNResult[1], 2)) + "ms")
                    print("Total Wait Time: " + str(round(SPNResult[2], 2)) + "ms")
                    print("Response Time: " + str(round(SPNResult[3], 2)) + "ms")
                    print("ThroughPut: " + str(round(SPNResult[4], 2)) + " per process")

                    option = input("continue? Y/N")
                    if option in ["N", "n"]:
                        quit()
                    else:
                        option = ""
                        continue

                else:
                    PRIResult = PRI()
                    print("Analysis for PRI: ")
                    print("CPU utilization: " + str(round(PRIResult[0] * 100, 2)) + "%")
                    print("Total Turn Around Time: " + str(round(PRIResult[1], 2)) + "ms")
                    print("Total Wait Time: " + str(round(PRIResult[2], 2)) + "ms")
                    print("Response Time: " + str(round(PRIResult[3], 2)) + "ms")
                    print("ThroughPut: " + str(round(PRIResult[4], 2)) + " per process")

                    option = input("continue? Y/N")
                    if option in ["N", "n"]:
                        quit()
                    else:
                        option = ""
                        continue

        else:
            print("File Don't Exist, Enter Again")
            fileName = str(input("Input File Name: "))


menu()
