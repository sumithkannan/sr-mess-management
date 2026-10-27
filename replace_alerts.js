const fs = require('fs');
const path = require('path');

const files = [
  'frontend/src/views/Users.vue',
  'frontend/src/views/Reports.vue',
  'frontend/src/views/Ratings.vue',
  'frontend/src/views/Menu.vue',
  'frontend/src/views/Expenses.vue',
  'frontend/src/views/Dashboard.vue',
  'frontend/src/views/Attendance.vue',
  'frontend/src/views/AdminConfig.vue'
];

for (const f of files) {
  const full = path.join('D:\\SR Mess Management', f);
  if (!fs.existsSync(full)) continue;
  let s = fs.readFileSync(full, 'utf8');
  if (!s.includes('useToast')) {
    if (s.includes("from '../api'")) {
      s = s.replace("from '../api'", "from '../api'\nimport { useToast } from '../composables/useToast'");
    } else if (s.includes('from \'../api\'')) {
      s = s.replace('from \'../api\'', 'from \'../api\'\nimport { useToast } from \'../composables/useToast\'');
    }
    // add toast instance after imports/script setup start
    if (s.includes('<script setup>')) {
      s = s.replace('<script setup>\n', '<script setup>\nconst toast = useToast()\n');
    }
  }
  s = s.replace(/alert\(([^)]*)\)/g, (m, p1) => {
    // skip if it's just a string we want to keep? but better convert
    if (p1.includes('confirm')) return m;
    return `toast.error(${p1})`;
  });
  // convert specific success/info alerts
  s = s.replace("toast.error('Updated')", "toast.success('Updated')");
  s = s.replace("toast.error('Image is compressing...')", "toast.info('Image is compressing...')");
  s = s.replace("toast.error('Failed to compress image')", "toast.error('Failed to compress image')");
  fs.writeFileSync(full, s);
  console.log('done', f);
}
