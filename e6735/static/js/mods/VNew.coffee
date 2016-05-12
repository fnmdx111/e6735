$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'
videojs = require 'video.js'
shortid = require 'shortid'

Uploader = React.createFactory(require './Uploader')
ScoreVector = React.createFactory(require './ScoreVector')
AbstractView = require './AbstractView'

E = require './Els'

SimplePanel = React.createFactory(require './SimplePanel')

preview_video = null

UPLOAD_URL = 'upload'

new_view_item = React.createClass
  render: ->
    $$p = this.props
    $$s = this.state ? {}

    __id = "preview-widget-#{$$p.id}"

    pv = if $$s.type?.match /video/
      E.div {
        id: __id
        ref: "target-#{$$p.id}"
        className: "embed-responsive embed-responsive-16by9 mm-container"
      }
      # Because video.js is not very compatible with react.js, we are going to
      # append <video> later to this div#__id

    else if $$s.type?.match /audio/
      audio_properties =
        className: 'embed-responsive-item'
        controls: true
        preload: 'auto'
        id: "audio-preview-#{$$p.id}"

      E.div {
        id: __id
        className: "embed-responsive embed-responsive-16by9 mm-container"
      },
        E.audio audio_properties,
          E.source {src: $$s.fp, type: $$s.type}
      # Audio tags are native HTML5 elements, work well with react.js
    else
      E.div {}
      # No preview

    preview = SimplePanel {id: "preview-#{$$p.id}", title: "Preview"}, pv

    E.div {id: "new-item-#{$$p.id}", className: "panel panel-default"},
      E.div {className: ""},
        E.div {className: "mm-container"},
          Uploader {
            url: $$p.url
            evt_hnds: $$p.evt_hnds
            auto_upload: false
          }
          E.hr {className: 'vnew'}
          E.div {className: "row"},
            E.div {className: "col-md-8"},
              preview
            ScoreVector {col: 4, id: $$p.id}
          E.div {className: "input-group"},
            E.input {
              type: "text"
              className: "form-control"
              placeholder: "Title"
              id: "title-input-#{$$p.id}"
              ariaDescribedby: "addon-by"
            }
            E.span {className: "input-group-addon", id: "addon-by-#{$$p.id}"},
              "by"
            E.input {
              type: "text"
              className: "form-control"
              placeholder: "Artist"
              id: "artist-input-#{$$p.id}"
              ariaDescribedby: "addon-by"
            }

  componentDidUpdate: ->
    $$s = @state ? {}
    $$p = @props
    if $$s.type?.match /video/
      wrapper = document.createElement 'div'
      wrapper.innerHTML = """<video
  id="video-preview-#{$$p.id}"
  class='video-js vjs-default-skin embed-responsive-item'
  preload='auto' controls height='322' width='640'>
  <source src='#{$$s.fp}' type='#{$$s.type}' />
</video>"""

      v = wrapper.firstChild
      $("#video-preview-#{$$p.id}").remove()
      @refs["target-#{@props.id}"].appendChild(v)
      videojs v, {}, ->
        preview_video = this

    else if $$s.type?.match /audio/
      preview_video?.reset().hide()

      a = document.getElementById('audio-preview')
      a?.load()

    true


new_view = React.createClass
  render: ->
    @state = {items: [], dzs: {}} if not @state?

    E.div {id: "new-view"},
          E.div {},
                E.h2 {}, "How do you like your stuffs?"
          E.div {id: "new-item-anchor"},
                @state.items
          E.div {className: "btn-group pull-right", role: "group"},
             E.btn {
               className: "btn btn-primary"
               id: "submit"
             }, "Submit"
             E.btn {
               id: "add-item"
               className: "btn btn-info"
             }, "+"
  componentDidMount: ->
    me = this
    me.state = {items: [], dzs: {}} unless me.state?

    build_new_item = ->
      el = [null]
      evt_hnds = {
        addedfile: (file) =>
          el[0].setState
            type: file.type
            fp: window.URL.createObjectURL file
        init: (dz) =>
          dzs = me.state.dzs
          dzs[el[0].props.id] = dz
          me.setState {dzs: dzs}
      }

      __id = shortid.generate()
      el[0] = React.createElement new_view_item, {
        url: UPLOAD_URL
        evt_hnds: evt_hnds
        id: __id
        key: __id
        ref: (x) -> el[0] = x
      }
      el[0]

    $('#add-item').on 'click', ->
      if me.state
        items = me.state.items
      else
        items = []

      n_item = build_new_item()
      items.push n_item
      me.setState({items: items})

    $('#submit').on 'click', ->
      $('.waiting').removeClass 'invisible'
      each = (item, id, data) ->
        title = $("#title-input-#{item.props.id}").val()
        artist = $("#artist-input-#{item.props.id}").val()

        if title == ""
          alert "Title cannot be empty!"
          $('.waiting').addClass 'invisible'
          return
        if artist == ""
          alert "Artist cannot be empty!"
          $('.waiting').addClass 'invisible'
          return

        data.append "file#{id}", me.state.dzs[item.props.id].files[0]
        data.append "dims#{id}",
                    ($("#dim-#{item.props.id}-#{ii}").val() / 100.0 for ii in [1..8])
        data.append "title#{id}", title
        data.append "artist#{id}", artist

      data = new FormData()
      data.append "n", me.state.items.length
      for item, i in me.state.items
        each item, i, data

      $.ajax {
               url: me.props.url
               data: data
               processData: false
               contentType: false
               type: "POST"
               success: (data) =>
                 $('.waiting').addClass 'invisible'
                 switch data.status
                   when 'failed'
                     alert "Upload failed! Reason: #{data.reason}."
                   when 'successful'
                     alert 'Upload successful!'
                     @hide()
                     @render()
               error: =>
                 $('.waiting').addClass 'invisible'
             }

module.exports = class VNew extends AbstractView
  constructor: (@url='/upload', anchor_id='upload') ->
    super '#' + anchor_id, anchor_id

  render: ->
    super()

    try ReactDOM.unmountComponentAtNode @anchor?
    el = React.createElement(new_view, {url: '/upload'})
    ReactDOM.render el, @anchor
