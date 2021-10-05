
# Code Question


## Setup

Clone this GIT repo to your machine.

On the project root folder:

```
conda env create -f environment.yml
docker-compose up -d
```

## Run
run the following command in your terminal with the api key for virustotal:
```
python run.py
usage: run.py [-h] --apikey APIKEY --file FILE [--reset-cache]
```

## Example output

```
(personal) ➜  elementor git:(master) ✗ python run.py --apikey xxx --file request1.csv --reset-cache
url is not fresh - fetching from VT...raneevahijab.id
url is not fresh - fetching from VT...www.google.com
url is not fresh - fetching from VT...www.textspeier.de
url is not fresh - fetching from VT...stackoverflow.com
url is not fresh - fetching from VT...www.family-partners.fr
url is not fresh - fetching from VT...www.facebook.com
url is not fresh - fetching from VT...www.elementor.com
url is not fresh - fetching from VT...www.wordpress.org
url is not fresh - fetching from VT...boots.fotopyra.pl
{   'boots.fotopyra.pl': SiteScan(is_risky=True),
    'raneevahijab.id': SiteScan(is_risky=True),
    'stackoverflow.com': SiteScan(is_risky=False),
    'www.elementor.com': SiteScan(is_risky=False),
    'www.facebook.com': SiteScan(is_risky=False),
    'www.family-partners.fr': SiteScan(is_risky=True),
    'www.google.com': SiteScan(is_risky=True),
    'www.textspeier.de': SiteScan(is_risky=True),
    'www.wordpress.org': SiteScan(is_risky=False)}
(personal) ➜  elementor git:(master) ✗ python run.py --apikey xxx --file request1.csv
{   'boots.fotopyra.pl': SiteScan(is_risky=True),
    'raneevahijab.id': SiteScan(is_risky=True),
    'stackoverflow.com': SiteScan(is_risky=False),
    'www.elementor.com': SiteScan(is_risky=False),
    'www.facebook.com': SiteScan(is_risky=False),
    'www.family-partners.fr': SiteScan(is_risky=True),
    'www.google.com': SiteScan(is_risky=True),
    'www.textspeier.de': SiteScan(is_risky=True),
    'www.wordpress.org': SiteScan(is_risky=False)}
```

## Implementation

I used a Redis cache memory to store cache scans from VirusTotal.
I set an experiation time for the keys for 15 minutes like required.
This way, Redis will flush my scan results after this time without
any code required.

- step 1 - read input urls
- step 2 - fetch results from cache if exists
- step 3 - fetch what we are missing from VT

## Things I didn't have time for
- I didn't fetch the voting information
- I would do the scan parallel with asyncio
- I would write the API you requested
    - The API will probably have timeouts because IO takes long time (maybe tweak the nginx to bigger timeout)
- On AWS, I would do a serverless solution for this: API Gateway with Lambda
- For cache db we can use RDS redis instance, other options available also.
- no proper error handling
- i didn't write tests with mock responses to check out different network conditions
- yaml file for configuration


# SQL Question

## Question
Employee question - you have the following tables: 
-	employees: employee_id, first_name, last_name, hire_date, salary, manager_id, department_id
-	departments: department_id, department_name, location_id
We would like to know for each department top earning employee, salary, difference
from the second earning employee.


## Answer
What I did:
 - find max salary for each department
 - calculate the differneces in sallaries based on order in department
 - join it and pick up only the top salary employee for each department
 - if there are two employees with the same salary - the apear together in the result
I didn't run this. Hope it works :) 

```
WITH (
    SELECT 
    d.department_id as department_id,
    max(salary) as max_salary
    FROM employee as e
    GROUP by department_id
) AS departments_max_salaries;

WITH (
    SELECT 
        department_id,
        employee_id,
        salary
        salary - LEAD(salary)
            OVER (ORDER BY salary DESC ) AS salary_diff
    FROM employee as e
    GROUP by department_id
    ORDER BY salary DESC, employee_id
) AS employees_w_diff_salary;

SELECT d.department_id, e.employee_id, e.salary, e.salary_diff
FROM departments_max_salaries d, employees_w_diff_salary e 
WHERE  
    d.department_id = e.department_id 
    AND e.salary = d.max_salary;

```


