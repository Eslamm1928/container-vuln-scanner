import axios from 'axios';

export const getScans = async (apiUrl) => {
  const response = await axios.get(`${apiUrl}/scans`);
  return response.data;
};

export const submitScan = async (apiUrl, imageName) => {
  const response = await axios.post(`${apiUrl}/scan`, {
    image_name: imageName
  });
  return response.data;
};

export const getVulnerabilities = async (apiUrl, scanId) => {
  const response = await axios.get(`${apiUrl}/scans/${scanId}/vulnerabilities`);
  return response.data;
};




