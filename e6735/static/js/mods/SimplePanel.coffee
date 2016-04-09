React = require 'react'

[_div, _h4] = (React.createFactory(name) for name in ['div', 'h4'])

module.exports = React.createClass
  render:  ->
    title_el = if @props.title_el?
      @props.title_el.className += ' panel-title'
    else
      _h4 {className: "panel-title"}, @props.title

    _div {id: @props.id ? ""},
      _div {className: "panel panel-#{@props.class_name ? "info"}"},
        _div {className: "panel-heading"},
          title_el
        _div {className: "panel-body"},
          @props.children

