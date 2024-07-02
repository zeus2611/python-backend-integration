// hubspot.js

import { useState } from 'react';
import {
    Box,
    Button,
    CircularProgress
} from '@mui/material';
import axios from 'axios';

export const HubSpotIntegration = ({ user, org, setIntegrationParams }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);

    // Function to open OAuth in a new window
    const handleConnectClick = async () => {
        try {
            setIsConnecting(true);
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/authorize`, formData);
            console.log(response);
            const authURL = response?.data;

            const newWindow = window.open(authURL, 'Hubspot Authorization', 'width=600, height=600');

            // Polling for the window to close
            const pollTimer = window.setInterval(() => {
                if (newWindow?.closed !== false) { 
                    window.clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 200);
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail);
        }
    }

    // Function to handle logic when the OAuth window closes
    const handleWindowClosed = async () => {
        try {
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/credentials`, formData);
            const credentials = response.data; 
            if (credentials) {
                setIsConnecting(false);
                setIsConnected(true);
                setIntegrationParams(prev => ({ ...prev, credentials: credentials, type: 'HubSpot' }));
            }
            setIsConnecting(false);
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail);
        }
    }

    return (
        <Box sx={{mt: 2}}>
            Parameters
            <Box display='flex' alignItems='center' justifyContent='center' sx={{mt: 2}}>
                {isConnected ? (
                    <Button 
                        variant='contained' 
                        color='success'
                        disabled={isConnecting}
                        style={{
                            pointerEvents: 'none',
                            cursor: 'default',
                            opacity: 1
                        }}
                    >
                        HubSpot Connected
                    </Button>
                ) : (
                    <Button 
                        variant='contained' 
                        onClick={handleConnectClick}
                        color='primary'
                        disabled={isConnecting}
                        style={{
                            pointerEvents: 'auto',
                            cursor: 'pointer',
                            opacity: isConnected ? 1 : undefined
                        }}
                    >
                        {isConnecting ? (
                            <CircularProgress size={20} />
                        ) : (
                            'Connect to HubSpot'
                        )}
                    </Button>
                )}
            </Box>
        </Box>
    );
}
