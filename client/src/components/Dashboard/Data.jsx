import axios from 'axios';
import { saveAs } from 'file-saver';
import React, { useEffect, useState } from 'react';
import * as XLSX from 'xlsx';

import Loading from '../Loading/Loading';
import './Data.css';

const Data = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        axios.get('http://localhost:5000/getdata')
            .then((response) => {
                setData(response.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error('Error fetching data: ', error);
            });
    }, []);

    // Function to export data as Excel
    const exportToExcel = () => {
        const wsData = data?.data?.map((item) => [item.id, ...item.dates]);
        const ws = XLSX.utils.aoa_to_sheet([['ID\\Date', ...data?.unique_dates], ...wsData]);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Data');
        const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        saveAs(blob, 'attendance.xlsx');
    };

    // Function to calculate total absents for each student
    const calculateTotalStudentAbsents = (studentIndex) => {
        return data?.data[studentIndex]?.dates.reduce((total, item) => {
            return total + (item ? 0 : 1);
        }, 0);
    };


    const Less = async () => {
        try {
            await axios.post('http://localhost:5000/sendmaillees');
            alert('mail sent');
        }
        catch (err) {
            console.log(err);
        }
    };

    const All = async () => {
        try {
            await axios.post('http://localhost:5000/sendmailall');
            alert('mail sent');
        }
        catch (err) {
            console.log(err);
        }
    };

    // Calculate total presents for each date
    const calculateTotalDatePresents = (dateIndex) => {
        return data?.data.reduce((total, student) => {
            return total + (student?.dates[dateIndex] ? 1 : 0);
        }, 0);
    };

    return (
        loading ? <Loading /> :
            <div className='data'>
                <div className='buttons-div'>

                    <button className='btn' onClick={exportToExcel} style={{
                        // center the button
                        margin: '0 auto',
                        display: 'block',
                        marginTop: '20px',
                    }}> Export to Excel</button>
                    <button className='btn' onClick={All} style={{
                        // center the button
                        margin: '0 auto',
                        display: 'block',
                        marginTop: '20px',
                    }}>Mail all</button>
                    <button className='btn' onClick={Less} style={{
                        // center the button
                        margin: '0 auto',
                        display: 'block',
                        marginTop: '20px',
                    }}> Mail less than 85%</button>
                </div>
                <table className='data-table'>
                    <thead>
                        <tr>
                            <th key={-1}>
                                ID \ Date
                            </th>
                            {
                                data?.unique_dates?.map((item, index) => (
                                    <th key={index}>{item}</th>
                                ))
                            }
                            <th>Total Absents</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                            data?.data?.map((item, studentIndex) => {
                                return (
                                    <tr key={studentIndex}>
                                        <td key={-1}>{item?.id}</td>
                                        {
                                            item?.dates?.map((item, dateIndex) => (
                                                <td key={dateIndex}>{item ? 'P' : 'A'}</td>
                                            ))
                                        }
                                        <td>{calculateTotalStudentAbsents(studentIndex)}</td>
                                    </tr>
                                );
                            })
                        }
                    </tbody>
                    <tfoot>
                        <tr>
                            <td key={-1}>Total Presents</td>
                            {
                                data?.unique_dates?.map((item, dateIndex) => (
                                    <td key={dateIndex}>{calculateTotalDatePresents(dateIndex)}</td>
                                ))
                            }
                        </tr>
                    </tfoot>
                </table>
            </div>
    );
};

export default Data;
