
ReactDOM = require 'react-dom'
$ = require 'jquery'

module.exports = class AbstractView
  constructor: (@show_hide_selector, @render_anchor_id) ->
    @shown = false

  refresh_refs: ->
    @anchor = document.getElementById @render_anchor_id
    @$el = $ @show_hide_selector

  render: ->
    @shown = true
    @$el?.removeClass 'invisible'

  hide: ->
    @shown = false
    @$el?.addClass 'invisible'
    ReactDOM.unmountComponentAtNode @anchor
