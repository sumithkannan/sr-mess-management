const fs = require('fs');
const p = 'D:\\SR Mess Management\\frontend\\src\\views\\Expenses.vue';
let s = fs.readFileSync(p, 'utf8');
const old = "  } catch (e) {\n    toast.error(\"Couldn't compress image. Please use a smaller JPG/PNG or pick from gallery.\")\n    imageFile.value = null\n    imagePreview.value = ''\n    imageSizeText.value = ''\n    compressing.value = false\n  }";
const neu = "  } catch (e) {\n    toast.error(\"Couldn't compress this photo. Try lowering camera resolution or pick a smaller JPG/PNG from gallery.\")\n    imageFile.value = null\n    imagePreview.value = ''\n    imageSizeText.value = ''\n    compressing.value = false\n  }";
if (s.indexOf(old) >= 0) {
  s = s.split(old).join(neu);
  fs.writeFileSync(p, s);
  console.log('ok');
} else {
  console.log('no');
}
