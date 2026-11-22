(() => {
  const get = selector => document.querySelector(selector);
  const editor = get('#editor');
  const status = get('[data-status]');
  const saveButton = get('button[type=submit]');
  const publishButton = get('#publish');
  const course = get('#course');
  const fields = {
    intro: get('#course-intro'),
    task: get('#course-task'),
    note: get('#course-note'),
  };
  let model, defaults, revision;
  let dirty = false;

  function report(message, error = false) {
    status.textContent = message;
    status.classList.toggle('text-danger', error);
  }

  async function api(url, method = 'GET', data) {
    const options = method === 'GET' ? {} : {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    };
    const response = await fetch(url, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || '请求失败。');
    return result;
  }

  function selectCourse() {
    const override = model.courses[course.value] || {};
    for (const [key, field] of Object.entries(fields)) {
      field.value = override[key] || '';
      field.placeholder = defaults[course.value][key] || '可留空';
    }
  }

  function addEntry(entry) {
    const fragment = get('#entry-template').content.cloneNode(true);
    const fieldset = fragment.querySelector('.entry');
    for (const input of fieldset.querySelectorAll('[data-field]')) input.value = entry[input.dataset.field] || '';
    fieldset.querySelector('[data-remove]').addEventListener('click', () => {
      fieldset.remove();
      dirty = true;
      report('有未保存的更改。');
    });
    get('#entries').append(fragment);
    return fieldset;
  }

  function collect() {
    model.cover_title = get('#cover-title').value;
    model.signature = get('#signature').value;
    model.entries = Array.from(document.querySelectorAll('.entry')).map(section =>
      Object.fromEntries(Array.from(section.querySelectorAll('[data-field]')).map(field => [field.dataset.field, field.value]))
    );
    return model;
  }

  async function save() {
    const result = await api('/api/content', 'PUT', { data: collect(), revision });
    revision = result.revision;
    dirty = false;
  }

  function busy(value) {
    saveButton.disabled = value;
    publishButton.disabled = value;
    get('#fields').disabled = value;
  }

  course.addEventListener('change', selectCourse);
  for (const [key, field] of Object.entries(fields)) {
    field.addEventListener('input', () => {
      if (!model.courses[course.value]) model.courses[course.value] = {};
      model.courses[course.value][key] = field.value;
    });
  }
  editor.addEventListener('input', () => {
    dirty = true;
    report('有未保存的更改。');
  });
  get('#new-entry').addEventListener('click', () => {
    addEntry({ category: '项目' }).querySelector('[data-field=title]').focus();
    dirty = true;
    report('有未保存的更改。');
  });

  editor.addEventListener('submit', async event => {
    event.preventDefault();
    busy(true);
    try {
      await save();
      report('草稿已保存。可以打开预览。');
    } catch(error) {
      report(error.message, true);
    } finally { busy(false); }
  });
  publishButton.addEventListener('click', async () => {
    if (!editor.reportValidity() || !window.confirm('将当前作品集内容发布到 x-ing.xyz？')) return;
    busy(true);
    try {
      if (dirty) await save();
      report('正在提交到 GitHub…');
      const result = await api('/api/publish', 'POST', { revision });
      report(result.message);
    } catch(error) {
      report(error.message, true);
    } finally { busy(false); }
  });

  api('/api/content').then(result => {
    model = result.data;
    revision = result.revision;
    defaults = result.courses;
    get('#cover-title').value = model.cover_title;
    get('#signature').value = model.signature;
    for (const [slug, item] of Object.entries(defaults)) course.add(new Option(item.title, slug));
    selectCourse();
    for (const [stage, description] of Object.entries(result.plan)) {
      const label = document.createElement('label');
      label.className = 'd-block mb-2';
      label.textContent = stage;
      const input = document.createElement('textarea');
      input.className = 'form-control';
      input.maxLength = 450;
      input.placeholder = description;
      input.value = model.plan[stage] || '';
      input.addEventListener('input', () => { model.plan[stage] = input.value; });
      label.append(input);
      get('#plan').append(label);
    }
    for (const entry of model.entries) addEntry(entry);
    busy(false);
    report('可以编辑当前草稿。');
  }).catch(error => report(error.message, true));
})();
