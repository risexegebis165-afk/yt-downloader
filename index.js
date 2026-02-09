require('dotenv').config();
const express = require('express');
const multer = require('multer');
const PublitioAPI = require('publitio-sdk');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });
const publitio = new PublitioAPI(process.env.PUBLITIO_API_KEY, process.env.PUBLITIO_API_SECRET);

app.use(express.static('public'));

app.post('/upload', upload.single('file'), async (req, res) => {
    try {
        const data = await publitio.uploadFile(req.file.path, 'file', { privacy: '1' });
        
        // পাবলিটিও URL থেকে এক্সটেনশন আলাদা করা
        const fullUrl = data.url_preview;
        const urlWithoutExt = fullUrl.substring(0, fullUrl.lastIndexOf('.'));

        // কোয়ালিটি ট্রান্সফরমেশন লিংক
        const links = {
            v360p: urlWithoutExt.replace('/file/', '/file/dl,w_640,h_360/') + '.mp4',
            v720p: urlWithoutExt.replace('/file/', '/file/dl,w_1280,h_720/') + '.mp4',
            mp3: urlWithoutExt.replace('/file/', '/file/dl,q_80/') + '.mp3'
        };

        res.json({ success: true, links });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
});

app.listen(process.env.PORT || 3000, () => console.log("Server Started!"));
