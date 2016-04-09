
React = require 'react'
Dropzone = React.createFactory(require 'react-dropzone-component')

module.exports = React.createClass
  render: ->
    $$p = this.props

    Dropzone {
      config: {
        iconFiletypes: ['mp4', 'mp3', 'ogg']
        showFiletypeIcon: true
        postUrl: $$p.url
      }
      djsConfig: {
        autoProcessQueue: if $$p.auto_upload? then $$p.auto_upload else true
      }
      eventHandlers: {
        init: (dz) =>
          $$p.evt_hnds.init? dz

          dz.options.accept = (file, done) ->
            while this.files.length > 1
              this.removeFile(this.files[0])
            $$p.evt_hnds.accept? file
            done()
          dz.options.acceptedFiles = 'video/*,audio/*'

        addedfile: $$p.evt_hnds.addedfile
        sending: $$p.evt_hnds.sending
        complete: $$p.evt_hnds.complete
        success: $$p.evt_hnds.success
        canceled: $$p.evt_hnds.canceled
      }
    }
