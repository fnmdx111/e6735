React = require 'react'

els = [
  'span', 'input', 'button', 'img', 'h2', 'hr', 'div', 'p', 'video',
  'audio', 'ul', 'li', 'a',
  'source', 'h4', 'h5',
  'label']

exp = {}

for name in els
  exp[name] = React.createFactory name

exp.btn = React.createFactory 'button'

module.exports = exp
