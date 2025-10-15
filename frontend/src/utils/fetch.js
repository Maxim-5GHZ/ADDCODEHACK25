const API_BASE = '/api';

async function healthCheck() {
    return fetch(`${API_BASE}/health`);
}

async function getLogs(password) {
    return fetch(`${API_BASE}/log?password=${encodeURIComponent(password)}`);
}

async function getMainPage() {
    return fetch(`${API_BASE}/`);
}

async function validateToken(token) {
    try {
        const response = await fetch(`${API_BASE}/users/profile?token=${encodeURIComponent(token)}`);
        
        if (!response.ok) {
            return false;
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            return data.status === 'success';
        }
        
        return false;
    } catch (error) {
        console.error('Token validation error:', error);
        return false;
    }
}

async function getToken(login, password) {
    try {
        const response = await fetch(
            `${API_BASE}/get_token?login=${encodeURIComponent(login)}&password=${encodeURIComponent(password)}`
        );
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === "success") {
            return data.token;
        } else {
            throw new Error(data.message || "Failed to get token");
        }
    } catch (error) {
        console.error('Error getting token:', error);
        throw error;
    }
}


async function registerUser(login, password, firstName, lastName) {
    return fetch(`${API_BASE}/add_user?login=${encodeURIComponent(login)}&password=${encodeURIComponent(password)}&first_name=${encodeURIComponent(firstName)}&last_name=${encodeURIComponent(lastName)}`, {
        method: 'POST'
    });
}

async function getAllUsers(password) {
    return fetch(`${API_BASE}/users/all?password=${encodeURIComponent(password)}`);
}

async function getUserProfile(token) {
    return fetch(`${API_BASE}/users/profile?token=${encodeURIComponent(token)}`);
}

async function saveField(token, fieldName, areaOfInterest) {
    return fetch(`${API_BASE}/fields/save?token=${encodeURIComponent(token)}&field_name=${encodeURIComponent(fieldName)}&area_of_interest=${encodeURIComponent(areaOfInterest)}`, {
        method: 'POST'
    });
}

async function getFieldsList(token) {
    return fetch(`${API_BASE}/fields/list?token=${encodeURIComponent(token)}`);
}

async function deleteField(fieldId, token) {
    return fetch(`${API_BASE}/fields/${encodeURIComponent(fieldId)}?token=${encodeURIComponent(token)}`, {
        method: 'DELETE'
    });
}

// Функции анализа
async function performAnalysis(token, startDate, endDate, options) {
    let url = `${API_BASE}/analysis/perform?token=${encodeURIComponent(token)}&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`;
    
    if (options.lon && options.lat && options.radius_km) {
        url += `&lon=${encodeURIComponent(options.lon)}&lat=${encodeURIComponent(options.lat)}&radius_km=${encodeURIComponent(options.radius_km)}`;
    } else if (options.polygonCoords) {
        url += `&polygon_coords=${encodeURIComponent(JSON.stringify(options.polygonCoords))}`;
    }
    
    return fetch(url, { method: 'POST' });
}

async function getAnalysisList(token) {
    return fetch(`${API_BASE}/analysis/list?token=${encodeURIComponent(token)}`);
}

async function getAnalysisById(analysisId, token) {
    return fetch(`${API_BASE}/analysis/${encodeURIComponent(analysisId)}?token=${encodeURIComponent(token)}`);
}

async function deleteAnalysis(analysisId, token) {
    return fetch(`${API_BASE}/analysis/${encodeURIComponent(analysisId)}?token=${encodeURIComponent(token)}`, {
        method: 'DELETE'
    });
}

// Устаревшие функции пользовательских данных
async function saveUserData(token, keyArray) {
    return fetch(`${API_BASE}/savedata?token=${encodeURIComponent(token)}&key_array=${encodeURIComponent(JSON.stringify(keyArray))}`, {
        method: 'POST'
    });
}

async function getUserData(token) {
    return fetch(`${API_BASE}/givefield?token=${encodeURIComponent(token)}`);
}

async function updateUserData(token, newKeyArray) {
    return fetch(`${API_BASE}/data/update?token=${encodeURIComponent(token)}&key_array=${encodeURIComponent(JSON.stringify(newKeyArray))}`, {
        method: 'PUT'
    });
}

async function partialUpdateUserData(token, keysToAdd = [], keysToRemove = []) {
    return fetch(`${API_BASE}/data/edit?token=${encodeURIComponent(token)}&keys_to_add=${encodeURIComponent(JSON.stringify(keysToAdd))}&keys_to_remove=${encodeURIComponent(JSON.stringify(keysToRemove))}`, {
        method: 'PATCH'
    });
}

async function checkUserDataExists(token) {
    return fetch(`${API_BASE}/data/check?token=${encodeURIComponent(token)}`);
}

async function deleteUserData(token) {
    return fetch(`${API_BASE}/data/delete?token=${encodeURIComponent(token)}`, {
        method: 'DELETE'
    });
}

// Устаревшие функции данных полей
async function setFieldData(field, data, token) {
    return fetch(`${API_BASE}/field/set?field=${encodeURIComponent(field)}&data=${encodeURIComponent(data)}&token=${encodeURIComponent(token)}`, {
        method: 'POST'
    });
}

async function getFieldData(field) {
    return fetch(`${API_BASE}/field/get?field=${encodeURIComponent(field)}`);
}

async function checkFieldExists(field) {
    return fetch(`${API_BASE}/field/check?field=${encodeURIComponent(field)}`);
}

async function deleteFieldData(field, token) {
    return fetch(`${API_BASE}/field/delete?field=${encodeURIComponent(field)}&token=${encodeURIComponent(token)}`, {
        method: 'DELETE'
    });
}

// Устаревшие функции получения изображений
async function getRgbImage(lon, lat, startDate, endDate, token) {
    return fetch(`${API_BASE}/image/rgb?lon=${encodeURIComponent(lon)}&lat=${encodeURIComponent(lat)}&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}&token=${encodeURIComponent(token)}`);
}

async function getRedChannelImage(lon, lat, startDate, endDate, token) {
    return fetch(`${API_BASE}/image/red-channel?lon=${encodeURIComponent(lon)}&lat=${encodeURIComponent(lat)}&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}&token=${encodeURIComponent(token)}`);
}

async function getNdviImage(lon, lat, startDate, endDate, token) {
    return fetch(`${API_BASE}/image/ndvi?lon=${encodeURIComponent(lon)}&lat=${encodeURIComponent(lat)}&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}&token=${encodeURIComponent(token)}`);
}

export {
    healthCheck,
    getLogs,
    getMainPage,
    validateToken,
    getToken,
    registerUser,
    getAllUsers,
    getUserProfile,
    saveField,
    getFieldsList,
    deleteField,
    performAnalysis,
    getAnalysisList,
    getAnalysisById,
    deleteAnalysis,
    saveUserData,
    getUserData,
    updateUserData,
    partialUpdateUserData,
    checkUserDataExists,
    deleteUserData,
    setFieldData,
    getFieldData,
    checkFieldExists,
    deleteFieldData,
    getRgbImage,
    getRedChannelImage,
    getNdviImage
};