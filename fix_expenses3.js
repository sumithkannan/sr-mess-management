const fs = require('fs');
const p = 'D:\\SR Mess Management\\frontend\\src\\views\\Expenses.vue';
let s = fs.readFileSync(p, 'utf8');

// Replace the whole function
const start = s.indexOf('async function compressImage');
const end = s.indexOf('\nasync function handleImageSelect');
if (start === -1 || end === -1) { console.log('bad'); process.exit(); }

const neu = `async function compressImage(file) {
  compressing.value = true
  try {
    const maxSize = 2 * 1024 * 1024
    if (file.size <= maxSize) {
      imageFile.value = file
      imagePreview.value = URL.createObjectURL(file)
      imageSizeText.value = \`Original: \${(file.size/1024).toFixed(0)}KB\`
      compressing.value = false
      return
    }
    
    if (file.type === 'image/heic' || file.type === 'image/heif' || file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif')) {
      toast.error('HEIC images cannot be compressed in browser. Please convert to JPG/PNG or use a smaller image.')
      imageFile.value = null
      imagePreview.value = ''
      imageSizeText.value = ''
      compressing.value = false
      return
    }
    
    toast.info('Image is compressing...')
    
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        const tryCompress = (maxDim, startQuality) => {
          const canvas = document.createElement('canvas')
          let width = img.width
          let height = img.height
          if (width > maxDim || height > maxDim) {
            const ratio = Math.min(maxDim / width, maxDim / height)
            width = Math.round(width * ratio)
            height = Math.round(height * ratio)
          }
          canvas.width = width
          canvas.height = height
          const ctx = canvas.getContext('2d')
          ctx.drawImage(img, 0, 0, width, height)
          
          const compress = (quality, dims) => {
            canvas.toBlob((blob) => {
              if (!blob) {
                if (dims === 1024) tryCompress(800, 0.7)
                else if (dims === 800) tryCompress(640, 0.6)
                else if (dims === 640) tryCompress(512, 0.5)
                else {
                  toast.error("This photo is too large to compress. Lower your camera resolution in phone settings, or pick a smaller image from gallery.")
                  imageFile.value = null
                  imagePreview.value = ''
                  imageSizeText.value = ''
                  compressing.value = false
                  resolve()
                }
                return
              }
              if (blob.size > maxSize && quality > 0.25) {
                compress(quality - 0.1, dims)
              } else if (blob.size > maxSize) {
                if (dims === 1024) tryCompress(800, 0.7)
                else if (dims === 800) tryCompress(640, 0.6)
                else if (dims === 640) tryCompress(512, 0.5)
                else {
                  toast.error("This photo is too large to compress. Lower your camera resolution in phone settings, or pick a smaller image from gallery.")
                  imageFile.value = null
                  imagePreview.value = ''
                  imageSizeText.value = ''
                  compressing.value = false
                  resolve()
                }
              } else {
                const compressedFile = new File([blob], 'bill.jpg', { type: 'image/jpeg' })
                imageFile.value = compressedFile
                imagePreview.value = URL.createObjectURL(compressedFile)
                imageSizeText.value = \`Compressed: \${(blob.size/1024).toFixed(0)}KB\`
                compressing.value = false
                resolve()
              }
            }, 'image/jpeg', quality)
          }
          compress(startQuality, maxDim)
        }
        tryCompress(800, 0.7)
      }
      img.onerror = () => {
        toast.error("Couldn't compress this photo. Try lowering camera resolution or pick a smaller JPG/PNG from gallery.")
        imageFile.value = null
        imagePreview.value = ''
        imageSizeText.value = ''
        compressing.value = false
        resolve()
      }
      img.src = URL.createObjectURL(file)
    })
  } catch (e) {
    toast.error("Couldn't compress this photo. Try lowering camera resolution or pick a smaller JPG/PNG from gallery.")
    imageFile.value = null
    imagePreview.value = ''
    imageSizeText.value = ''
    compressing.value = false
  }
}
`;

s = s.slice(0, start) + neu + s.slice(end);
fs.writeFileSync(p, s);
console.log('ok');
